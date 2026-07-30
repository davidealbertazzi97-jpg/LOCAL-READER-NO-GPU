from __future__ import annotations

import json
import shutil
import threading
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Any

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from .config import MAX_UPLOAD_BYTES, PATHS
from .documents import load_document, validate_document, write_exports
from .engines import ENGINES
from .engines.speech import verified_kokoro
from .jobs import RUNNER
from .product import PRODUCT
from .security import (
    TOKEN_COOKIE,
    origin_is_allowed,
    request_is_authorized,
    request_is_loopback,
    token_matches,
)
from .store import STORE
from .utils import remove_output_tree, remove_work_tree, resolve_artifact, safe_name

STATIC = PATHS.app / "static"
CHUNK_SIZE = 1024 * 1024
MAX_DOCUMENT_EDIT_BYTES = 12 * 1024 * 1024
DOCUMENT_LOCK = threading.Lock()


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
        "connect-src 'self'; "
        "font-src 'self'; "
        "img-src 'self' data:; "
        "media-src 'self'; "
        "object-src 'none'; "
        "base-uri 'none'; "
        "frame-ancestors 'none'; "
        "form-action 'self'"
    )
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response


@app.get("/health")
def health() -> dict[str, str]:
    return {"app": PRODUCT.slug, "status": "ok", "version": PRODUCT.version}


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
    model_ready = False
    if tts_ready:
        try:
            verified_kokoro()
            model_ready = True
        except RuntimeError:
            model_ready = False
    return {
        "ocr": {
            "ready": ocr_ready,
            "engine": "RapidOCR PP-OCRv6 small / ONNX CPU",
        },
        "speech": {
            "ready": tts_ready and model_ready,
            "engine": "Kokoro ONNX INT8 / CPU",
            "voices": ["im_nicola", "if_sara"],
            "piper": False,
        },
    }


@app.get("/api/jobs")
def list_jobs() -> list[dict[str, Any]]:
    return [public_job(job) for job in STORE.list()]


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


@app.post("/api/jobs/{job_id}/speech", status_code=202)
async def create_speech(job_id: str, request: Request) -> dict[str, Any]:
    body = await limited_body(request, 4096, "Speech options")
    try:
        options = json.loads(body or b"{}")
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HTTPException(400, "Speech options must be valid JSON") from exc
    if not isinstance(options, dict):
        raise HTTPException(400, "Speech options must be an object")
    voice = options.get("voice", "im_nicola")
    speed = options.get("speed", 1.0)
    if voice not in {"im_nicola", "if_sara"}:
        raise HTTPException(400, "Unsupported Italian voice")
    if not isinstance(speed, (int, float)) or not 0.75 <= float(speed) <= 1.5:
        raise HTTPException(400, "Speech speed must be between 0.75 and 1.5")
    if not PATHS.tts_python.is_file():
        raise HTTPException(503, "The local Kokoro environment is not installed")
    try:
        verified_kokoro()
    except RuntimeError as exc:
        raise HTTPException(503, "Verified Kokoro files are not installed") from exc
    parent, source = completed_artifact(job_id, "reading.txt")
    if parent["engine"] != "accessible-document":
        raise HTTPException(404, "Accessible document not found")

    child = RUNNER.submit(
        "kokoro-italian",
        "reading.txt",
        {"voice": voice, "speed": float(speed), "source_job": job_id},
    )
    child_id = str(child["id"])
    work_dir = PATHS.work / child_id
    try:
        with DOCUMENT_LOCK:
            work_dir.mkdir(mode=0o700, parents=True, exist_ok=False)
            with (
                source.open("rb") as input_handle,
                (work_dir / "reading.txt").open("xb") as output_handle,
            ):
                shutil.copyfileobj(input_handle, output_handle, length=CHUNK_SIZE)
        child = STORE.mark_queued(child_id)
        RUNNER.enqueue(child_id)
        return public_job(child)
    except Exception:
        remove_work_tree(work_dir)
        STORE.update(
            child_id,
            status="failed",
            message="Speech preparation failed",
            error="The reviewed text could not be copied into the private job.",
        )
        raise


@app.get("/api/jobs/{job_id}/files/{artifact:path}")
def download_artifact(job_id: str, artifact: str):
    _, path = completed_artifact(job_id, artifact)
    if path.suffix.casefold() in {".webp", ".wav"}:
        return FileResponse(path)
    return FileResponse(path, filename=path.name)
