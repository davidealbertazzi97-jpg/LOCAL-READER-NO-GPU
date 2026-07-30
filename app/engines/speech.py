from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from ..config import PATHS
from ..processes import run_worker
from ..speech_jobs import normalized_options
from .base import EngineResult, LocalEngine

MODEL_HASHES = {
    "6e742170d309016e5891a994e1ce1559c702a2ccd0075e67ef7157974f6406cb",
    "7d5df8ecf7d4b1878015a32686053fd0eebe2bc377234608764cc0ef3636a6c5",
}
VOICES_HASH = "bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d"


@lru_cache(maxsize=8)
def _digest(
    path: str,
    size: int,
    modified_ns: int,
    changed_ns: int,
    inode: int,
) -> str:
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
    if (
        _digest(
            str(model),
            model_stat.st_size,
            model_stat.st_mtime_ns,
            model_stat.st_ctime_ns,
            model_stat.st_ino,
        )
        not in MODEL_HASHES
    ):
        raise RuntimeError("Kokoro model checksum is not approved")
    if (
        _digest(
            str(voices),
            voices_stat.st_size,
            voices_stat.st_mtime_ns,
            voices_stat.st_ctime_ns,
            voices_stat.st_ino,
        )
        != VOICES_HASH
    ):
        raise RuntimeError("Kokoro voice checksum is not approved")
    return model, voices


class KokoroSpeechEngine(LocalEngine):
    engine_id = "kokoro-italian"
    label_en = "Italian and English speech with Kokoro"
    label_it = "Voce italiana e inglese con Kokoro"
    description_en = (
        "Create natural Italian, American English, or British English speech "
        "locally with Kokoro on CPU."
    )
    description_it = (
        "Crea in locale una voce naturale italiana, inglese americana o inglese "
        "britannica con Kokoro su CPU."
    )
    accepted_extensions = frozenset({".txt"})
    user_upload = False

    def process(
        self,
        source: Path,
        output_dir: Path,
        options: dict[str, Any],
    ) -> EngineResult:
        if not PATHS.tts_python.is_file():
            raise RuntimeError("the isolated Kokoro environment is not installed")
        model, voices = verified_kokoro()
        voice, speed, language = normalized_options(
            options.get("voice", "im_nicola"),
            options.get("speed", 1.0),
            options.get("language", "it"),
        )

        output_dir.mkdir(parents=True, exist_ok=True)
        command = [
            str(PATHS.tts_python),
            str(PATHS.app / "workers" / "speech_worker.py"),
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
        completed = run_worker(
            command,
            cwd=PATHS.app,
            timeout=6 * 60 * 60,
        )
        if completed.returncode:
            raise RuntimeError("isolated Kokoro worker failed")
        audio = output_dir / "speech.wav"
        report = output_dir / "speech.json"
        if not audio.is_file() or not report.is_file():
            raise RuntimeError("Kokoro worker did not produce its declared output")
        summary = json.loads(report.read_text(encoding="utf-8"))
        return EngineResult(summary=summary, artifacts=(audio, report))


ENGINE = KokoroSpeechEngine()
