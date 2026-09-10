from __future__ import annotations

import hashlib
import json
import os
import tempfile
from functools import lru_cache
from pathlib import Path
from typing import Any

from ..config import PATHS
from ..processes import run_worker
from ..provider_config import speech_runtime_config
from ..speech_jobs import normalized_options
from .base import EngineResult, LocalEngine

MODEL_HASHES = {
    "6e742170d309016e5891a994e1ce1559c702a2ccd0075e67ef7157974f6406cb",
    "7d5df8ecf7d4b1878015a32686053fd0eebe2bc377234608764cc0ef3636a6c5",
}
VOICES_HASH = "bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d"


@lru_cache(maxsize=8)
def _digest(path: str, size: int, modified_ns: int, changed_ns: int, inode: int) -> str:
    del size, modified_ns, changed_ns, inode
    value = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def verified_kokoro() -> tuple[Path, Path]:
    model = PATHS.kokoro_model.resolve()
    voices = PATHS.kokoro_voices.resolve()
    if not model.is_file() or not voices.is_file():
        raise RuntimeError("Kokoro model files are not installed")
    model_stat = model.stat()
    voices_stat = voices.stat()
    model_hash = _digest(
        str(model),
        model_stat.st_size,
        model_stat.st_mtime_ns,
        model_stat.st_ctime_ns,
        model_stat.st_ino,
    )
    if model_hash not in MODEL_HASHES:
        raise RuntimeError("Kokoro model checksum is not approved")
    voices_hash = _digest(
        str(voices),
        voices_stat.st_size,
        voices_stat.st_mtime_ns,
        voices_stat.st_ctime_ns,
        voices_stat.st_ino,
    )
    if voices_hash != VOICES_HASH:
        raise RuntimeError("Kokoro voice checksum is not approved")
    return model, voices


def edge_environment() -> dict[str, str]:
    """Allow only the Edge-TTS child to reach Microsoft's speech endpoint."""
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment.pop("LD_PRELOAD", None)
    environment["PYTHONNOUSERSITE"] = "1"
    return environment


def external_environment() -> dict[str, str]:
    """Give only an isolated child process network access for a cloud provider."""
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment.pop("LD_PRELOAD", None)
    environment["PYTHONNOUSERSITE"] = "1"
    return environment


class EdgeSpeechEngine(LocalEngine):
    engine_id = "edge-tts"
    label_en = "Premium neural speech with Edge-TTS"
    label_it = "Voce neurale premium con Edge-TTS"
    description_en = "Create long Italian or English audio in bounded chunks."
    description_it = "Crea audio italiani o inglesi lunghi a blocchi controllati."
    accepted_extensions = frozenset({".txt"})
    user_upload = False

    def process(
        self,
        source: Path,
        output_dir: Path,
        options: dict[str, Any],
    ) -> EngineResult:
        if not PATHS.tts_python.is_file():
            raise RuntimeError("the isolated speech environment is not installed")
        provider = str(options.get("provider", "edge-tts"))
        voice = str(options.get("voice", ""))
        speed = float(options.get("speed", 1.0))
        language = str(options.get("language", "it"))
        if provider == "edge-tts":
            voice, speed, language = normalized_options(
                voice or "it-IT-GiuseppeMultilingualNeural",
                speed,
                language,
            )
        elif not 0.75 <= speed <= 1.5 or language not in {"it", "en-us", "en-gb"}:
            raise RuntimeError("speech options are invalid")
        output_dir.mkdir(parents=True, exist_ok=True)
        if provider == "edge-tts":
            command = [
                str(PATHS.tts_python),
                str(PATHS.app / "workers" / "speech_worker.py"),
                "--input",
                str(source),
                "--output",
                str(output_dir),
                "--voice",
                voice,
                "--speed",
                str(speed),
                "--language",
                language,
            ]
            environment = edge_environment()
        elif provider == "kokoro":
            model, voices = verified_kokoro()
            configured = speech_runtime_config(provider)
            default_voice = configured.get(
                "voice_it" if language == "it" else "voice_en", "if_sara"
            )
            voice = voice or str(default_voice)
            command = [
                str(PATHS.tts_python),
                str(PATHS.app / "workers" / "kokoro_worker.py"),
                "--input",
                str(source),
                "--output",
                str(output_dir),
                "--model",
                str(model),
                "--voices",
                str(voices),
                "--voice",
                voice,
                "--speed",
                str(speed),
                "--language",
                language,
            ]
            environment = edge_environment()
        elif provider in {"voxtral", "fish", "elevenlabs"}:
            configured = speech_runtime_config(provider)
            configured["provider"] = provider
            configured["voice_id"] = voice or str(configured.get("voice_id", ""))
            configured["speed"] = speed
            fd, config_name = tempfile.mkstemp(
                prefix=".speech-provider-", suffix=".json", dir=PATHS.data
            )
            config_path = Path(config_name)
            try:
                if os.name != "nt":
                    os.chmod(config_path, 0o600)
                with os.fdopen(fd, "w", encoding="utf-8") as handle:
                    json.dump(configured, handle, ensure_ascii=False)
                command = [
                    str(PATHS.tts_python),
                    str(PATHS.app / "workers" / "cloud_tts_worker.py"),
                    "--input",
                    str(source),
                    "--output",
                    str(output_dir),
                    "--config",
                    str(config_path),
                ]
                completed = run_worker(
                    command,
                    cwd=PATHS.app,
                    timeout=12 * 60 * 60,
                    env=external_environment(),
                )
            finally:
                config_path.unlink(missing_ok=True)
            if completed.returncode:
                raise RuntimeError("external speech provider failed")
            return self._result(output_dir, provider)
        else:
            raise RuntimeError("unknown speech provider")
        completed = run_worker(
            command, cwd=PATHS.app, timeout=12 * 60 * 60, env=environment
        )
        if completed.returncode:
            raise RuntimeError(f"{provider} speech worker failed")
        return self._result(output_dir, provider)

    @staticmethod
    def _result(output_dir: Path, provider: str) -> EngineResult:
        audio = output_dir / "speech.mp3"
        report = output_dir / "speech.json"
        if not audio.is_file() or not report.is_file():
            raise RuntimeError("speech worker did not produce its declared output")

        summary = json.loads(report.read_text(encoding="utf-8"))
        summary.setdefault("provider", provider)
        return EngineResult(summary=summary, artifacts=(audio, report))


ENGINE = EdgeSpeechEngine()
