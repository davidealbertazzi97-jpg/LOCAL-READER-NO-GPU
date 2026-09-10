from __future__ import annotations

import json
import os
import platform
import tempfile
import threading
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Any

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware import Middleware

from .body_limit import RequestBodyLimitMiddleware
from .config import MAX_UPLOAD_BYTES, PATHS
from .documents import load_document, validate_document, write_exports
from .engines import ENGINES
from .engines.speech import external_environment
from .jobs import RUNNER
from .processes import run_worker
from .product import PRODUCT
from .provider_config import (
    AI_PROVIDER_PRESETS,
    TTS_PROVIDER_INFO,
    add_clone,
    ai_config_for,
    load_settings,
    public_settings,
    save_settings,
    speech_runtime_config,
    valid_url,
)
from .reflow_jobs import queue_reflow_job
from .security import (
    TOKEN_COOKIE,
    origin_is_allowed,
    request_is_authorized,
    request_is_loopback,
    token_matches,
)
from .speech_jobs import (
    VOICE_LANGUAGES,
    queue_speech_job,
    resolved_options,
)
from .store import STORE
from .utils import remove_output_tree, remove_work_tree, resolve_artifact, safe_name

STATIC = PATHS.app / "static"
CHUNK_SIZE = 1024 * 1024
MAX_DOCUMENT_EDIT_BYTES = 12 * 1024 * 1024
MAX_TEXT_INPUT_BYTES = 20 * 1024 * 1024
DOCUMENT_LOCK = threading.Lock()
MAX_UPLOAD_REQUEST_BYTES = max(MAX_UPLOAD_BYTES, MAX_TEXT_INPUT_BYTES) + 256 * 1024
TEXT_ENGINES = {"plain-text", "lfm-reflow"}
SPEECH_SOURCE_ENGINES = {"accessible-document", *TEXT_ENGINES}
SPEECH_PROVIDERS = set(TTS_PROVIDER_INFO)
REFLOW_PROVIDERS = set(AI_PROVIDER_PRESETS)
MODEL_INSTALL_LOCK = threading.Lock()
MODEL_INSTALL_STATE = {"status": "idle", "message": ""}


async def limited_body(request: Request, maximum: int, label: str) -> bytes:
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            declared = int(content_length)
        except ValueError as exc:
            raise HTTPException(400, "Invalid content length") from exc
        if declared < 0:
            raise HTTPException(400, "Invalid content length")
        if declared > maximum:
            raise HTTPException(413, f"{label} exceeds the local limit")
    chunks: list[bytes] = []
    total = 0
    async for chunk in request.stream():
        total += len(chunk)
        if total > maximum:
            raise HTTPException(413, f"{label} exceeds the local limit")
        chunks.append(chunk)
    return b"".join(chunks)


def public_job(job: dict[str, Any]) -> dict[str, Any]:
    visible = dict(job)
    visible.pop("options", None)
    return visible


def completed_artifact(job_id: str, artifact: str) -> tuple[dict[str, Any], Path]:
    job = STORE.get(job_id)
    if not job or job["status"] != "completed" or artifact not in job["artifacts"]:
        raise HTTPException(404, "Completed artifact not found")
    try:
        path = resolve_artifact(PATHS.outputs / job_id, artifact)
    except ValueError as exc:
        raise HTTPException(404, "Completed artifact not found") from exc
    return job, path


def normalized_processing_options(
    engine: str,
    options: dict[str, Any],
) -> dict[str, Any]:
    if engine not in {"accessible-document", "plain-text"}:
        return options
    auto_speech = options.get("auto_speech", False)
    if not isinstance(auto_speech, bool):
        raise HTTPException(400, "auto_speech must be true or false")
    document_language = options.get("document_language", "it")
    speech_language = options.get(
        "speech_language",
        "it" if document_language == "it" else "en-us",
    )
    if not isinstance(document_language, str) or document_language not in {"it", "en"}:
        raise HTTPException(400, "document_language must be it or en")
    if not isinstance(speech_language, str):
        raise HTTPException(400, "speech_language must be a string")
    if (
        document_language == "it"
        and speech_language != "it"
        or document_language == "en"
        and speech_language not in {"en-us", "en-gb"}
    ):
        raise HTTPException(400, "speech language does not match the document")
    preserve_text = options.get("preserve_text", False)
    if not isinstance(preserve_text, bool):
        raise HTTPException(400, "preserve_text must be true or false")
    try:
        speech_provider, voice, speed, speech_language = resolved_options(
            options.get("voice", ""),
            options.get("speed", 1.0),
            speech_language,
            options.get("speech_provider"),
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return {
        "auto_speech": auto_speech,
        "preserve_text": preserve_text,
        "document_language": document_language,
        "speech_language": speech_language,
        "voice": voice,
        "speed": speed,
        "speech_provider": speech_provider,
    }


@asynccontextmanager
async def lifespan(_: FastAPI):
    RUNNER.start()
    yield
    RUNNER.stop()


app = FastAPI(
    title=PRODUCT.name,
    version=PRODUCT.version,
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan,
    middleware=[
        Middleware(
            RequestBodyLimitMiddleware,
            path=(
                "/api/jobs",
                "/api/text",
                "/api/settings",
                "/api/provider-models",
                "/api/voice-clones",
            ),
            maximum=MAX_UPLOAD_REQUEST_BYTES,
        )
    ],
)
app.mount("/assets", StaticFiles(directory=STATIC), name="assets")


@app.middleware("http")
async def local_security(request: Request, call_next):
    if not request_is_loopback(request):
        return JSONResponse({"detail": "Loopback access only"}, status_code=403)
    if request.url.path.startswith("/api/"):
        if not request_is_authorized(request):
            return JSONResponse({"detail": "Unauthorized local request"}, 401)
        if request.method not in {"GET", "HEAD", "OPTIONS"} and not origin_is_allowed(
            request
        ):
            return JSONResponse({"detail": "Invalid origin"}, 403)

    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self'; "
        "connect-src 'self'; "
        "font-src 'self'; "
        "img-src 'self' data:; "
        "media-src 'self'; "
        "worker-src 'none'; "
        "manifest-src 'none'; "
        "object-src 'none'; "
        "base-uri 'none'; "
        "frame-ancestors 'none'; "
        "form-action 'self'"
    )
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = (
        "camera=(), geolocation=(), microphone=(), payment=(), usb=()"
    )
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
    response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response


@app.get("/health")
def health() -> dict[str, str]:
    return {"app": PRODUCT.slug, "status": "ok", "version": PRODUCT.version}


@app.get("/api/local-models")
def local_models() -> dict[str, Any]:
    settings = public_settings()
    return {
        "selected": settings["ai"].get("local_model", "lfm"),
        "lfm": {"installed": PATHS.llama_model.is_file()},
        "gemma4": {
            "installed": PATHS.gemma_model.is_file(),
            "size": "5.2 GB",
            "license": "Apache-2.0",
        },
        "fish-local": {
            "installed": PATHS.mac_voice_python.is_file()
            and PATHS.fish_local_model.is_dir(),
            "size": "6.7 GB",
            "license": "Fish Audio Research License",
        },
        **MODEL_INSTALL_STATE,
    }


@app.post("/api/local-models/gemma4", status_code=202)
def install_gemma4() -> dict[str, str]:
    if load_settings()["tts"].get("offline_mode"):
        raise HTTPException(
            409, "Modalità offline attiva: riattivala per scaricare Gemma 4."
        )
    with MODEL_INSTALL_LOCK:
        if MODEL_INSTALL_STATE["status"] == "running":
            return {"status": "running", "message": "Download già in corso."}
        MODEL_INSTALL_STATE.update(
            status="running", message="Download Gemma 4 in corso…"
        )

    def download() -> None:
        import subprocess

        try:
            completed = subprocess.run(
                [
                    str(PATHS.tts_python),
                    str(PATHS.app / "scripts" / "install_gemma.py"),
                ],
                cwd=PATHS.app,
                check=False,
                capture_output=True,
                text=True,
                timeout=6 * 60 * 60,
                env=external_environment(),
            )
            if completed.returncode:
                raise RuntimeError("download failed")
            MODEL_INSTALL_STATE.update(status="ready", message="Gemma 4 è pronta.")
        except Exception:
            MODEL_INSTALL_STATE.update(
                status="error", message="Download Gemma 4 non riuscito."
            )

    threading.Thread(target=download, name="gemma-model-download", daemon=True).start()
    return {"status": "running", "message": MODEL_INSTALL_STATE["message"]}


@app.post("/api/local-models/fish-local", status_code=202)
def install_fish_local() -> dict[str, str]:
    if platform.system() != "Darwin" or platform.machine() != "arm64":
        raise HTTPException(400, "Fish Audio locale richiede macOS Apple Silicon.")
    with MODEL_INSTALL_LOCK:
        if MODEL_INSTALL_STATE["status"] == "running":
            return {"status": "running", "message": "Download già in corso."}
        MODEL_INSTALL_STATE.update(
            status="running", message="Preparo Fish Audio locale…"
        )

    def download() -> None:
        import subprocess

        try:
            completed = subprocess.run(
                [
                    str(PATHS.tts_python),
                    str(PATHS.app / "scripts" / "install_mac_fish.py"),
                ],
                cwd=PATHS.app,
                check=False,
                capture_output=True,
                text=True,
                timeout=12 * 60 * 60,
                env=external_environment(),
            )
            if completed.returncode:
                raise RuntimeError("download failed")
            MODEL_INSTALL_STATE.update(
                status="ready", message="Fish Audio locale è pronto."
            )
        except Exception:
            MODEL_INSTALL_STATE.update(
                status="error", message="Installazione Fish Audio non riuscita."
            )

    threading.Thread(target=download, name="fish-local-download", daemon=True).start()
    return {"status": "running", "message": MODEL_INSTALL_STATE["message"]}


@app.get("/")
def index(token: str | None = None):
    if token_matches(token):
        response = RedirectResponse("/", status_code=303)
        response.set_cookie(
            TOKEN_COOKIE,
            token,
            httponly=True,
            samesite="strict",
            secure=False,
            path="/",
        )
        return response
    return FileResponse(STATIC / "index.html")


@app.get("/legal")
def legal():
    return FileResponse(STATIC / "legal.html")


@app.get("/legal/license")
def legal_license():
    return FileResponse(PATHS.app / "LICENSE", filename="LICENSE")


@app.get("/legal/notices")
def legal_notices():
    return FileResponse(
        PATHS.app / "THIRD_PARTY_NOTICES.md",
        filename="THIRD_PARTY_NOTICES.md",
    )


@app.get("/legal/disclaimer")
def legal_disclaimer():
    return FileResponse(
        PATHS.app / "DISCLAIMER.md",
        filename="DISCLAIMER.md",
    )


@app.get("/api/product")
def product() -> dict[str, str]:
    return PRODUCT.public_dict()


@app.get("/api/engines")
def engines() -> list[dict[str, Any]]:
    return [engine.public_dict() for engine in ENGINES.values()]


@app.get("/api/status")
def status() -> dict[str, Any]:
    ocr_ready = PATHS.ocr_python.is_file()
    tts_ready = PATHS.tts_python.is_file()
    settings = public_settings()
    local_model = settings["ai"].get("local_model", "lfm")
    selected_reflow_model = (
        PATHS.gemma_model if local_model == "gemma4" else PATHS.llama_model
    )
    reflow_ready = PATHS.llama_cli.is_file() and selected_reflow_model.is_file()
    kokoro_ready = (
        tts_ready and PATHS.kokoro_model.is_file() and PATHS.kokoro_voices.is_file()
    )
    offline_mode = bool(settings["tts"].get("offline_mode", False))
    pocket_package = (
        PATHS.tts_python.parent.parent
        / ("Lib/site-packages" if os.name == "nt" else "lib/python3.12/site-packages")
        / "pocket_tts"
    )
    pocket_clone_ready = any(
        isinstance(item, dict)
        and item.get("provider") == "pocket-tts"
        and Path(str(item.get("reference_audio", ""))).is_file()
        for item in settings.get("clones", [])
    )
    tts_providers = {
        "edge-tts": {"ready": tts_ready, "network": True},
        "kokoro": {"ready": kokoro_ready, "network": False},
        "voxtral": {
            "ready": settings["tts"]["mistral"]["configured"],
            "network": True,
        },
        "fish": {
            "ready": settings["tts"]["fish"]["configured"],
            "network": True,
        },
        "fish-local": {
            "ready": (
                platform.system() == "Darwin"
                and platform.machine() == "arm64"
                and PATHS.mac_voice_python.is_file()
                and PATHS.fish_local_model.is_dir()
            ),
            "network": False,
        },
        "elevenlabs": {
            "ready": settings["tts"]["elevenlabs"]["configured"],
            "network": True,
        },
        "pocket-tts": {
            "ready": pocket_package.is_dir() and pocket_clone_ready,
            "network": False,
            "note": "richiede un campione audio e consenso esplicito",
        },
    }
    effective_speech_provider = (
        "kokoro" if offline_mode else settings["tts"]["default_provider"]
    )
    effective_speech = tts_providers.get(
        effective_speech_provider, tts_providers["edge-tts"]
    )
    speech_labels = {
        "edge-tts": "Microsoft Edge Neural TTS",
        "kokoro": "Kokoro 82M offline",
        "voxtral": "Voxtral TTS (Mistral)",
        "fish": "Fish Audio",
        "fish-local": "Fish Audio locale (Apple Silicon)",
        "elevenlabs": "ElevenLabs",
        "pocket-tts": "Pocket TTS",
    }
    return {
        "ocr": {
            "ready": ocr_ready,
            "engine": "PaddleOCR PP-OCRv6 / CPU",
        },
        "speech": {
            "ready": bool(effective_speech["ready"]),
            "engine": speech_labels.get(
                effective_speech_provider, effective_speech_provider
            ),
            "provider": effective_speech_provider,
            "offline": offline_mode,
            "voices": {
                language: sorted(voices) for language, voices in VOICE_LANGUAGES.items()
            },
            "network": "offline" if offline_mode else "Online providers may send text",
        },
        "providers": {
            "ai": {
                "presets": AI_PROVIDER_PRESETS,
                "configured": settings["ai"]["configured"],
                "selected": settings["ai"]["provider"],
                "configured_by_provider": settings["ai"].get("providers", {}),
            },
            "tts": {
                **tts_providers,
            },
        },
        "reflow": {
            "ready": reflow_ready,
            "engine": "Gemma 4 E4B Q4_0 / llama.cpp"
            if local_model == "gemma4"
            else "LFM2.5 230M / llama.cpp",
            "model": selected_reflow_model.name,
            "device": os.environ.get("LOCAL_ACCESSIBILITY_STUDIO_LFM_DEVICE", "auto"),
            "reasoning": "disabled",
        },
    }


@app.get("/api/settings")
def get_settings() -> dict[str, Any]:
    return {
        "settings": public_settings(),
        "ai_presets": AI_PROVIDER_PRESETS,
        "tts_providers": TTS_PROVIDER_INFO,
    }


@app.put("/api/settings")
async def put_settings(request: Request) -> dict[str, Any]:
    body = await limited_body(request, 64 * 1024, "Provider settings")
    try:
        payload = json.loads(body or b"{}")
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HTTPException(400, "Provider settings must be valid JSON") from exc
    try:
        return {"settings": save_settings(payload)}
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@app.post("/api/provider-models")
async def provider_models(request: Request) -> dict[str, Any]:
    if load_settings()["tts"].get("offline_mode"):
        raise HTTPException(
            409,
            "Modalità offline attiva: disattivala per contattare un servizio online.",
        )
    body = await limited_body(request, 64 * 1024, "Provider model request")
    try:
        payload = json.loads(body or b"{}")
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HTTPException(400, "Provider model request must be valid JSON") from exc
    if not isinstance(payload, dict):
        raise HTTPException(400, "Provider model request must be an object")

    provider = payload.get("provider", "")
    if not isinstance(provider, str) or provider not in AI_PROVIDER_PRESETS:
        raise HTTPException(400, "unknown AI provider")
    if provider == "local":
        return {
            "provider": provider,
            "models": [AI_PROVIDER_PRESETS[provider]["model"]],
        }

    settings = load_settings()
    api_key = payload.get("api_key", "")
    if not isinstance(api_key, str) or len(api_key) > 1024:
        raise HTTPException(400, "API key is invalid")
    api_key = api_key.strip() or str(settings["ai_keys"].get(provider, "")).strip()
    if not api_key:
        raise HTTPException(400, "Enter the provider API key first")

    if provider == "custom":
        base_url = payload.get("base_url", "")
        if not isinstance(base_url, str) or len(base_url) > 512:
            raise HTTPException(400, "Provider URL is invalid")
        base_url = base_url.strip()
        if not base_url and settings["ai"].get("provider") == "custom":
            base_url = str(settings["ai"].get("base_url", "")).strip()
        if not valid_url(base_url):
            raise HTTPException(400, "The custom provider URL must use HTTPS")
    else:
        base_url = AI_PROVIDER_PRESETS[provider]["base_url"]

    if not PATHS.tts_python.is_file():
        raise HTTPException(503, "The local worker environment is not installed")
    PATHS.data.mkdir(mode=0o700, parents=True, exist_ok=True)
    config_fd, config_name = tempfile.mkstemp(
        prefix=".provider-models-", suffix=".json", dir=PATHS.data
    )
    output_fd, output_name = tempfile.mkstemp(
        prefix=".provider-models-", suffix=".out", dir=PATHS.data
    )
    config_path = Path(config_name)
    output_path = Path(output_name)
    try:
        if os.name != "nt":
            os.chmod(config_path, 0o600)
            os.chmod(output_path, 0o600)
        with os.fdopen(config_fd, "w", encoding="utf-8") as handle:
            json.dump(
                {"provider": provider, "base_url": base_url, "api_key": api_key},
                handle,
                ensure_ascii=False,
            )
        os.close(output_fd)
        command = [
            str(PATHS.tts_python),
            str(PATHS.app / "workers" / "provider_models_worker.py"),
            "--config",
            str(config_path),
            "--output",
            str(output_path),
        ]
        environment = os.environ.copy()
        environment.pop("PYTHONPATH", None)
        environment.pop("LD_PRELOAD", None)
        environment["PYTHONNOUSERSITE"] = "1"
        completed = run_worker(
            command, cwd=PATHS.app, timeout=90, env=environment, network=True
        )
        if completed.returncode:
            raise HTTPException(502, "The provider model list could not be retrieved")
        try:
            result = json.loads(output_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise HTTPException(
                502, "The provider returned an invalid model list"
            ) from exc
        models = result.get("models") if isinstance(result, dict) else None
        if not isinstance(models, list) or not all(
            isinstance(model, str) for model in models
        ):
            raise HTTPException(502, "The provider returned an invalid model list")
        return {"provider": provider, "models": models}
    finally:
        config_path.unlink(missing_ok=True)
        output_path.unlink(missing_ok=True)


@app.post("/api/voice-clones", status_code=201)
async def create_voice_clone(
    provider: Annotated[str, Form()],
    name: Annotated[str, Form()],
    consent: Annotated[str, Form()],
    file: Annotated[UploadFile, File()],
    reference_text: Annotated[str, Form()] = "",
) -> dict[str, Any]:
    if load_settings()["tts"].get("offline_mode") and provider not in {
        "fish-local",
        "pocket-tts",
    }:
        raise HTTPException(
            409, "Modalità offline attiva: la clonazione cloud è disabilitata."
        )
    if provider in {"fish-local", "pocket-tts"}:
        if provider == "fish-local" and (
            platform.system() != "Darwin" or platform.machine() != "arm64"
        ):
            raise HTTPException(400, "Fish Audio locale richiede macOS Apple Silicon")
        if provider == "fish-local" and (
            not reference_text.strip() or len(reference_text) > 2_000
        ):
            raise HTTPException(
                400, "Inserisci il testo pronunciato nel campione audio"
            )
    elif provider not in {"voxtral", "elevenlabs"}:
        raise HTTPException(
            400, "Voice cloning is currently available for Voxtral and ElevenLabs"
        )
    if consent.casefold() not in {"true", "1", "yes", "on"}:
        raise HTTPException(
            400, "You must confirm that you have permission to use this voice"
        )
    safe_title = safe_name(name)[:120]
    if not safe_title:
        raise HTTPException(400, "Voice name is empty")
    suffix = Path(file.filename or "sample.wav").suffix.casefold()
    if suffix not in {".wav", ".mp3", ".m4a", ".ogg", ".flac", ".webm"}:
        raise HTTPException(
            415, "Choose an audio sample: WAV, MP3, M4A, OGG, FLAC or WEBM"
        )
    settings = load_settings()
    section_name = "mistral" if provider == "voxtral" else "elevenlabs"
    config = dict(settings["tts"].get(section_name, {}))
    if provider not in {"fish-local", "pocket-tts"} and not config.get("api_key"):
        raise HTTPException(503, "Configure the provider API key in Settings first")
    clone_dir = PATHS.data / "voice-clones"
    clone_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    sample_path = clone_dir / f".sample-{uuid.uuid4().hex}{suffix}"
    reference_path = clone_dir / f"reference-{uuid.uuid4().hex}{suffix}"
    result_path = clone_dir / f".result-{uuid.uuid4().hex}.json"
    received = 0
    try:
        with sample_path.open("xb") as handle:
            while chunk := await file.read(CHUNK_SIZE):
                received += len(chunk)
                if received > 25 * 1024 * 1024:
                    raise HTTPException(413, "The voice sample is too large")
                handle.write(chunk)
        if provider in {"fish-local", "pocket-tts"}:
            sample_path.replace(reference_path)
            clone = add_clone(
                provider=provider,
                name=safe_title,
                voice_id=f"{provider}-{uuid.uuid4().hex[:12]}",
                reference_audio=str(reference_path),
                reference_text=reference_text.strip(),
            )
            return {"clone": clone}
        fd, config_name = tempfile.mkstemp(
            prefix=".clone-provider-", suffix=".json", dir=PATHS.data
        )
        config_path = Path(config_name)
        try:
            if os.name != "nt":
                os.chmod(config_path, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(config, handle, ensure_ascii=False)
            command = [
                str(PATHS.tts_python),
                str(PATHS.app / "workers" / "cloud_clone_worker.py"),
                "--provider",
                provider,
                "--name",
                safe_title,
                "--sample",
                str(sample_path),
                "--config",
                str(config_path),
                "--output",
                str(result_path),
            ]
            completed = run_worker(
                command,
                cwd=PATHS.app,
                timeout=30 * 60,
                env=external_environment(),
                network=True,
            )
        finally:
            config_path.unlink(missing_ok=True)
        if completed.returncode or not result_path.is_file():
            raise HTTPException(502, "The provider could not create the voice clone")
        result = json.loads(result_path.read_text(encoding="utf-8"))
        voice_id = result.get("voice_id") if isinstance(result, dict) else None
        if not isinstance(voice_id, str) or not voice_id:
            raise HTTPException(502, "The provider returned no voice ID")
        clone = add_clone(provider=provider, name=safe_title, voice_id=voice_id)
        save_settings({"tts": {section_name: {"voice_id": voice_id}}})
        return {"clone": clone}
    except HTTPException:
        raise
    except (OSError, ValueError, RuntimeError) as exc:
        raise HTTPException(
            502, "The provider could not create the voice clone"
        ) from exc
    finally:
        sample_path.unlink(missing_ok=True)
        result_path.unlink(missing_ok=True)
        await file.close()


@app.get("/api/jobs")
def list_jobs() -> list[dict[str, Any]]:
    return [public_job(job) for job in STORE.list()]


@app.delete("/api/jobs")
def delete_finished_jobs() -> dict[str, int]:
    deleted = 0
    with DOCUMENT_LOCK:
        for job_id in STORE.finished_ids():
            remove_output_tree(PATHS.outputs / job_id)
            if STORE.delete_finished(job_id):
                deleted += 1
    return {"deleted": deleted}


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str) -> dict[str, Any]:
    job = STORE.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return public_job(job)


@app.delete("/api/jobs/{job_id}")
def delete_job(job_id: str) -> dict[str, bool]:
    job = STORE.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    if job["status"] not in {"completed", "failed"}:
        raise HTTPException(409, "An active job cannot be deleted")
    with DOCUMENT_LOCK:
        remove_output_tree(PATHS.outputs / job_id)
        if not STORE.delete_finished(job_id):
            raise HTTPException(409, "Job state changed; reload the list")
    return {"deleted": True}


@app.post("/api/jobs", status_code=202)
async def create_job(
    engine: Annotated[str, Form()],
    file: Annotated[UploadFile, File()],
    options: Annotated[str, Form()] = "{}",
) -> dict[str, Any]:
    selected = ENGINES.get(engine)
    if selected is None:
        raise HTTPException(400, "Unknown engine")
    if not selected.user_upload:
        raise HTTPException(400, "This engine does not accept direct uploads")
    if engine == "accessible-document" and not PATHS.ocr_python.is_file():
        raise HTTPException(503, "The local OCR environment is not installed")
    if len(options.encode("utf-8")) > 16 * 1024:
        raise HTTPException(413, "Options exceed the configured local limit")
    try:
        parsed_options = json.loads(options)
    except ValueError as exc:
        raise HTTPException(400, "Options must be valid JSON") from exc
    if not isinstance(parsed_options, dict):
        raise HTTPException(400, "Options must be a JSON object")
    parsed_options = normalized_processing_options(engine, parsed_options)

    input_name = safe_name(file.filename or "document")
    if not selected.accepts(Path(input_name)):
        raise HTTPException(415, "File extension not accepted by this engine")

    job = RUNNER.submit(engine, input_name, parsed_options)
    job_id = str(job["id"])
    work_dir = PATHS.work / job_id
    destination = work_dir / input_name
    total = 0
    try:
        work_dir.mkdir(mode=0o700, parents=True, exist_ok=False)
        with destination.open("xb") as handle:
            while chunk := await file.read(CHUNK_SIZE):
                total += len(chunk)
                if total > MAX_UPLOAD_BYTES:
                    raise HTTPException(413, "File exceeds the configured local limit")
                handle.write(chunk)
        job = STORE.mark_queued(job_id)
        RUNNER.enqueue(job_id)
        return public_job(job)
    except Exception:
        remove_work_tree(work_dir)
        STORE.update(
            job_id,
            status="failed",
            message="Upload failed",
            error="The private working copy could not be stored.",
        )
        raise
    finally:
        await file.close()


@app.post("/api/text", status_code=202)
async def create_text_job(request: Request) -> dict[str, Any]:
    body = await limited_body(request, MAX_TEXT_INPUT_BYTES, "Text input")
    try:
        payload = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HTTPException(400, "Text input must be valid JSON") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("text"), str):
        raise HTTPException(400, "Text input must contain a text string")
    text = payload["text"]
    if not text.strip():
        raise HTTPException(400, "Text input is empty")
    if len(text.encode("utf-8")) > MAX_TEXT_INPUT_BYTES:
        raise HTTPException(413, "Text input exceeds the local limit")
    raw_options = payload.get("options", payload)
    if not isinstance(raw_options, dict):
        raise HTTPException(400, "Text options must be an object")
    options = normalized_processing_options("plain-text", raw_options)
    title = safe_name(str(payload.get("title", "testo-incollato.txt")))
    if Path(title).suffix.casefold() not in {".txt", ".text", ".md", ".markdown"}:
        title = f"{title}.txt"

    job = RUNNER.submit("plain-text", title, options)
    job_id = str(job["id"])
    work_dir = PATHS.work / job_id
    destination = work_dir / title
    try:
        work_dir.mkdir(mode=0o700, parents=True, exist_ok=False)
        with destination.open("xb") as handle:
            handle.write(text.encode("utf-8"))
        job = STORE.mark_queued(job_id)
        RUNNER.enqueue(job_id)
        return public_job(job)
    except Exception:
        remove_work_tree(work_dir)
        STORE.update(
            job_id,
            status="failed",
            message="Text input failed",
            error="The private text copy could not be stored.",
        )
        raise


@app.get("/api/jobs/{job_id}/document")
def get_document(job_id: str) -> dict[str, Any]:
    job, path = completed_artifact(job_id, "document.json")
    if job["engine"] != "accessible-document":
        raise HTTPException(404, "Accessible document not found")
    try:
        return load_document(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise HTTPException(500, "Stored document is invalid") from exc


@app.put("/api/jobs/{job_id}/document")
async def update_document(job_id: str, request: Request) -> dict[str, Any]:
    body = await limited_body(request, MAX_DOCUMENT_EDIT_BYTES, "Document edit")
    try:
        submitted = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HTTPException(400, "Document edit must be valid JSON") from exc
    job, path = completed_artifact(job_id, "document.json")
    if job["engine"] != "accessible-document":
        raise HTTPException(404, "Accessible document not found")
    try:
        with DOCUMENT_LOCK:
            current = load_document(path)
            if (
                not isinstance(submitted, dict)
                or submitted.get("revision") != current["revision"]
            ):
                raise HTTPException(409, "Document was already changed; reload it")
            submitted["revision"] = current["revision"] + 1
            validated = validate_document(submitted)
            return write_exports(path.parent, validated)
    except HTTPException:
        raise
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise HTTPException(400, str(exc)) from exc


def completed_text_source(job_id: str) -> tuple[dict[str, Any], Path]:
    job, path = completed_artifact(job_id, "reading.txt")
    if job["engine"] not in SPEECH_SOURCE_ENGINES:
        raise HTTPException(404, "Reading text not found")
    return job, path


@app.get("/api/jobs/{job_id}/text")
def get_text(job_id: str) -> dict[str, str]:
    job, path = completed_text_source(job_id)
    try:
        return {
            "title": str(job["input_name"]),
            "text": path.read_text(encoding="utf-8"),
        }
    except OSError as exc:
        raise HTTPException(500, "Stored reading text is unavailable") from exc


@app.put("/api/jobs/{job_id}/text")
async def update_text(job_id: str, request: Request) -> dict[str, str]:
    body = await limited_body(request, MAX_TEXT_INPUT_BYTES, "Text edit")
    try:
        submitted = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HTTPException(400, "Text edit must be valid JSON") from exc
    if not isinstance(submitted, dict) or not isinstance(submitted.get("text"), str):
        raise HTTPException(400, "Text edit must contain a text string")
    text = submitted["text"]
    if not text.strip():
        raise HTTPException(400, "Text edit is empty")
    if len(text.encode("utf-8")) > MAX_TEXT_INPUT_BYTES:
        raise HTTPException(413, "Text edit exceeds the local limit")
    job, path = completed_text_source(job_id)
    if job["engine"] not in TEXT_ENGINES:
        raise HTTPException(404, "Only text jobs can be edited here")
    temporary = path.with_suffix(path.suffix + ".tmp")
    try:
        with DOCUMENT_LOCK:
            temporary.write_text(text, encoding="utf-8")
            temporary.replace(path)
        return {"title": str(job["input_name"]), "text": text}
    except OSError as exc:
        temporary.unlink(missing_ok=True)
        raise HTTPException(500, "Text could not be saved locally") from exc


@app.post("/api/jobs/{job_id}/reflow", status_code=202)
async def create_reflow(job_id: str, request: Request) -> dict[str, Any]:
    body = await limited_body(request, 4096, "Reflow options")
    try:
        options = json.loads(body or b"{}")
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HTTPException(400, "Reflow options must be valid JSON") from exc
    if not isinstance(options, dict):
        raise HTTPException(400, "Reflow options must be an object")
    device = options.get(
        "device",
        os.environ.get("LOCAL_ACCESSIBILITY_STUDIO_LFM_DEVICE", "auto"),
    )
    if not isinstance(device, str) or device not in {"auto", "cpu", "gpu"}:
        raise HTTPException(400, "device must be auto, cpu, or gpu")
    provider = options.get("provider", "local")
    if load_settings()["tts"].get("offline_mode"):
        provider = "local"
    if not isinstance(provider, str) or provider not in REFLOW_PROVIDERS:
        raise HTTPException(400, "unknown organization provider")
    if not PATHS.tts_python.is_file():
        raise HTTPException(503, "The local worker environment is not installed")
    selected_model_name = load_settings()["ai"].get("local_model", "lfm")
    selected_model = (
        PATHS.gemma_model if selected_model_name == "gemma4" else PATHS.llama_model
    )
    if provider == "local" and (
        not PATHS.llama_cli.is_file() or not selected_model.is_file()
    ):
        label = "Gemma 4" if selected_model_name == "gemma4" else "LFM2.5"
        raise HTTPException(503, f"llama.cpp and the {label} model are not installed")
    if provider != "local":
        try:
            ai_config_for(provider)
        except ValueError as exc:
            raise HTTPException(503, str(exc)) from exc
    _, source = completed_text_source(job_id)
    try:
        with DOCUMENT_LOCK:
            child = queue_reflow_job(
                RUNNER,
                STORE,
                source,
                source_job=job_id,
                device=device,
                provider=provider,
            )
        return public_job(child)
    except ValueError as exc:
        raise HTTPException(413, "Text exceeds the reflow limit") from exc
    except (OSError, RuntimeError) as exc:
        raise HTTPException(500, "Reflow could not be queued locally") from exc


@app.post("/api/jobs/{job_id}/speech", status_code=202)
async def create_speech(job_id: str, request: Request) -> dict[str, Any]:
    body = await limited_body(request, 4096, "Speech options")
    try:
        options = json.loads(body or b"{}")
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HTTPException(400, "Speech options must be valid JSON") from exc
    if not isinstance(options, dict):
        raise HTTPException(400, "Speech options must be an object")
    try:
        provider, voice, speed, language = resolved_options(
            options.get("voice", ""),
            options.get("speed", 1.0),
            options.get("language", "it"),
            options.get("provider"),
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    if not PATHS.tts_python.is_file():
        raise HTTPException(503, "The isolated speech environment is not installed")
    if provider == "kokoro" and (
        not PATHS.kokoro_model.is_file() or not PATHS.kokoro_voices.is_file()
    ):
        raise HTTPException(503, "Kokoro model or voices are not installed")
    if provider == "pocket-tts":
        pocket_ready = public_settings()["providers"]["tts"]["pocket-tts"]["ready"]
        if not pocket_ready:
            raise HTTPException(503, "Installa il componente Pocket TTS prima dell'uso")
        voice = voice or ""
        clone = next(
            (
                item
                for item in load_settings().get("clones", [])
                if isinstance(item, dict)
                and item.get("provider") == provider
                and item.get("voice_id") == voice
            ),
            None,
        )
        if not clone or not Path(str(clone.get("reference_audio", ""))).is_file():
            raise HTTPException(400, "Scegli una voce Pocket TTS clonata")
    if provider in {"voxtral", "fish", "elevenlabs"}:
        try:
            speech_runtime_config(provider)
        except ValueError as exc:
            raise HTTPException(503, str(exc)) from exc
    _, source = completed_text_source(job_id)

    try:
        with DOCUMENT_LOCK:
            child = queue_speech_job(
                RUNNER,
                STORE,
                source,
                source_job=job_id,
                voice=voice,
                speed=speed,
                language=language,
                provider=provider,
            )
        return public_job(child)
    except ValueError as exc:
        raise HTTPException(413, "Reading text exceeds the speech limit") from exc
    except (OSError, RuntimeError) as exc:
        raise HTTPException(500, "Speech could not be queued locally") from exc


@app.get("/api/jobs/{job_id}/files/{artifact:path}")
def download_artifact(job_id: str, artifact: str):
    _, path = completed_artifact(job_id, artifact)
    if path.suffix.casefold() in {".webp", ".wav", ".mp3"}:
        return FileResponse(path)
    return FileResponse(path, filename=path.name)
