from __future__ import annotations

import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

from .product import APP_ROOT, PRODUCT


def _platform_roots() -> tuple[Path, Path, Path]:
    home = Path.home()
    if os.name == "nt":
        local = Path(os.environ.get("LOCALAPPDATA", home / "AppData" / "Local"))
        data = local / PRODUCT.name
        state = data / "state"
    elif sys.platform == "darwin":
        data = home / "Library" / "Application Support" / PRODUCT.name
        state = home / "Library" / "Caches" / PRODUCT.name
    else:
        data_home = Path(
            os.environ.get("XDG_DATA_HOME", home / ".local" / "share")
        ).expanduser()
        state_home = Path(
            os.environ.get("XDG_STATE_HOME", home / ".local" / "state")
        ).expanduser()
        data = data_home / PRODUCT.slug
        state = state_home / PRODUCT.slug

    documents = home / "Documents"
    if not documents.is_dir() and (home / "Documenti").is_dir():
        documents = home / "Documenti"
    return data, state, documents / f"{PRODUCT.name} - Results"


def _private_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    if os.name != "nt":
        path.chmod(0o700)


@dataclass(frozen=True)
class Paths:
    app: Path
    data: Path
    work: Path
    outputs: Path
    state: Path
    database: Path
    ocr_python: Path
    tts_python: Path
    llama_cli: Path
    llama_model: Path
    gemma_model: Path
    mac_voice_python: Path
    fish_local_model: Path
    kokoro_model: Path
    kokoro_voices: Path

    @classmethod
    def build(cls) -> Paths:
        default_data, default_state, default_outputs = _platform_roots()
        prefix = PRODUCT.slug.upper().replace("-", "_")
        data = Path(os.environ.get(f"{prefix}_DATA", default_data)).expanduser()
        state = Path(os.environ.get(f"{prefix}_STATE", default_state)).expanduser()
        outputs = Path(
            os.environ.get(f"{prefix}_OUTPUTS", default_outputs)
        ).expanduser()
        executable = "python.exe" if os.name == "nt" else "python"
        scripts_dir = "Scripts" if os.name == "nt" else "bin"
        executable_suffix = ".exe" if os.name == "nt" else ""
        llama_candidates = []
        configured_cli = os.environ.get("LOCAL_READER_NO_GPU_LLAMA_CLI")
        if configured_cli:
            llama_candidates.append(Path(configured_cli).expanduser())
        llama_candidates.extend(
            (
                APP_ROOT / "bin" / f"llama-cli{executable_suffix}",
                APP_ROOT / "bin" / f"llama-completion{executable_suffix}",
            )
        )
        system_completion = shutil.which("llama-completion")
        if system_completion:
            llama_candidates.append(Path(system_completion))
        system_cli = shutil.which("llama-cli")
        if system_cli:
            llama_candidates.append(Path(system_cli))
        llama_candidates.extend(
            [
                Path.home()
                / "llama.cpp"
                / "build"
                / "bin"
                / f"llama-completion{executable_suffix}",
                Path.home()
                / "llama.cpp"
                / "build-local-reader"
                / "bin"
                / f"llama-completion{executable_suffix}",
                Path.home()
                / "llama.cpp"
                / "build"
                / "bin"
                / f"llama-cli{executable_suffix}",
                Path.home()
                / "llama.cpp"
                / "build-local-reader"
                / "bin"
                / f"llama-cli{executable_suffix}",
                Path.home()
                / "llama.cpp"
                / "build-cuda"
                / "bin"
                / f"llama-cli{executable_suffix}",
            ]
        )
        configured_model = os.environ.get("LOCAL_READER_NO_GPU_LFM_MODEL")
        model_candidates = []
        if configured_model:
            model_candidates.append(Path(configured_model).expanduser())
        model_candidates.extend(
            (
                APP_ROOT / "models" / "lfm" / "LFM2.5-230M-Q4_K_M.gguf",
                APP_ROOT / "models" / "lfm" / "LFM2.5-230M-Q8_0.gguf",
            )
        )
        configured_gemma_model = os.environ.get("LOCAL_READER_NO_GPU_GEMMA_MODEL")
        gemma_candidates = []
        if configured_gemma_model:
            gemma_candidates.append(Path(configured_gemma_model).expanduser())
        gemma_candidates.append(
            APP_ROOT / "models" / "gemma4" / "gemma-4-E4B_q4_0-it.gguf"
        )
        model_candidates.extend(
            (
                Path.home()
                / ".lmstudio"
                / "models"
                / "LiquidAI"
                / "LFM2.5-230M-GGUF"
                / "LFM2.5-230M-Q4_K_M.gguf",
                Path.home()
                / ".lmstudio"
                / "models"
                / "LiquidAI"
                / "LFM2.5-230M-GGUF"
                / "LFM2.5-230M-Q8_0.gguf",
            )
        )
        kokoro_model_candidates = []
        configured_kokoro_model = os.environ.get("LOCAL_READER_NO_GPU_KOKORO_MODEL")
        if configured_kokoro_model:
            kokoro_model_candidates.append(Path(configured_kokoro_model).expanduser())
        kokoro_model_candidates.extend(
            (
                APP_ROOT / "models" / "kokoro" / "kokoro-v1.0.onnx",
                APP_ROOT / "models" / "kokoro" / "kokoro-v1.0.int8.onnx",
            )
        )
        kokoro_voice_candidates = []
        configured_kokoro_voices = os.environ.get("LOCAL_READER_NO_GPU_KOKORO_VOICES")
        if configured_kokoro_voices:
            kokoro_voice_candidates.append(Path(configured_kokoro_voices).expanduser())
        kokoro_voice_candidates.extend(
            (
                APP_ROOT / "models" / "kokoro" / "voices-v1.0.bin",
                Path.home()
                / ".cache"
                / "hyperframes"
                / "tts"
                / "voices"
                / "voices-v1.0.bin",
            )
        )
        paths = cls(
            app=APP_ROOT,
            data=data,
            work=data / "work",
            outputs=outputs,
            state=state,
            database=data / "jobs.sqlite3",
            ocr_python=APP_ROOT / ".venv-ocr" / scripts_dir / executable,
            tts_python=APP_ROOT / ".venv-tts" / scripts_dir / executable,
            llama_cli=next(
                (path for path in llama_candidates if path.is_file()),
                llama_candidates[0],
            ),
            llama_model=next(
                (path for path in model_candidates if path.is_file()),
                model_candidates[0],
            ),
            gemma_model=next(
                (path for path in gemma_candidates if path.is_file()),
                gemma_candidates[0],
            ),
            mac_voice_python=APP_ROOT / ".venv-mac-voice" / scripts_dir / executable,
            fish_local_model=APP_ROOT / "models" / "fish-local",
            kokoro_model=next(
                (path for path in kokoro_model_candidates if path.is_file()),
                kokoro_model_candidates[0],
            ),
            kokoro_voices=next(
                (path for path in kokoro_voice_candidates if path.is_file()),
                kokoro_voice_candidates[0],
            ),
        )
        for directory in (paths.data, paths.work, paths.outputs, paths.state):
            _private_directory(directory)
        return paths


PATHS = Paths.build()
ACCESS_TOKEN = os.environ.get("LOCAL_AI_APP_TOKEN", "")
HOST = "127.0.0.1"
PORT = int(os.environ.get("LOCAL_AI_APP_PORT", "8765"))
MAX_UPLOAD_BYTES = int(
    os.environ.get("LOCAL_AI_APP_MAX_UPLOAD_BYTES", str(512 * 1024**2))
)
