from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Protocol

from .config import PATHS
from .store import JobStore
from .utils import remove_work_tree

VOICE_LANGUAGES = {
    "it": {"im_nicola", "if_sara"},
    "en-us": {"am_michael", "af_heart"},
    "en-gb": {"bm_george", "bf_emma"},
}
DEFAULT_VOICES = {
    "it": "im_nicola",
    "en-us": "am_michael",
    "en-gb": "bm_george",
}
MAX_SPEECH_SOURCE_BYTES = 2 * 1024 * 1024
COPY_CHUNK = 1024 * 1024


class SpeechQueue(Protocol):
    def submit(
        self,
        engine: str,
        input_name: str,
        options: dict[str, Any],
    ) -> dict[str, Any]: ...

    def enqueue(self, job_id: str) -> None: ...


def normalized_options(
    voice: Any,
    speed: Any,
    language: Any = "it",
) -> tuple[str, float, str]:
    selected_language = str(language)
    if selected_language not in VOICE_LANGUAGES:
        raise ValueError("unsupported speech language")
    selected_voice = str(voice)
    if selected_voice not in VOICE_LANGUAGES[selected_language]:
        raise ValueError("voice does not match the selected language")
    if isinstance(speed, bool):
        raise ValueError("invalid speech speed")
    try:
        selected_speed = float(speed)
    except (TypeError, ValueError) as exc:
        raise ValueError("invalid speech speed") from exc
    if not math.isfinite(selected_speed) or not 0.75 <= selected_speed <= 1.5:
        raise ValueError("speech speed must be between 0.75 and 1.5")
    return selected_voice, selected_speed, selected_language


def queue_speech_job(
    runner: SpeechQueue,
    store: JobStore,
    source: Path,
    *,
    source_job: str,
    voice: Any = "im_nicola",
    speed: Any = 1.0,
    language: Any = "it",
) -> dict[str, Any]:
    selected_voice, selected_speed, selected_language = normalized_options(
        voice,
        speed,
        language,
    )
    if not source.is_file():
        raise FileNotFoundError("reviewed reading text is missing")
    if source.stat().st_size > MAX_SPEECH_SOURCE_BYTES:
        raise ValueError("reviewed reading text exceeds the speech limit")

    child = runner.submit(
        "kokoro-italian",
        "reading.txt",
        {
            "voice": selected_voice,
            "speed": selected_speed,
            "language": selected_language,
            "source_job": source_job,
        },
    )
    child_id = str(child["id"])
    work_dir = PATHS.work / child_id
    try:
        work_dir.mkdir(mode=0o700, parents=True, exist_ok=False)
        received = 0
        with (
            source.open("rb") as input_handle,
            (work_dir / "reading.txt").open("xb") as output_handle,
        ):
            while chunk := input_handle.read(COPY_CHUNK):
                received += len(chunk)
                if received > MAX_SPEECH_SOURCE_BYTES:
                    raise ValueError("reviewed reading text exceeds the speech limit")
                output_handle.write(chunk)
        child = store.mark_queued(child_id)
        runner.enqueue(child_id)
        return child
    except Exception:
        remove_work_tree(work_dir)
        store.update(
            child_id,
            status="failed",
            message="Speech preparation failed",
            error="The reviewed text could not be copied into the private job.",
        )
        raise
