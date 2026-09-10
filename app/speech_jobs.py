from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Protocol

from .config import PATHS
from .provider_config import TTS_PROVIDER_INFO, load_settings
from .store import JobStore
from .utils import remove_work_tree

VOICE_LANGUAGES = {
    "it": {
        "it-IT-GiuseppeMultilingualNeural",
        "it-IT-ElsaNeural",
    },
    "en-us": {
        "en-US-AndrewMultilingualNeural",
        "en-US-AvaMultilingualNeural",
    },
    "en-gb": {
        "en-GB-RyanNeural",
        "en-GB-SoniaNeural",
    },
}
DEFAULT_VOICES = {
    "it": "it-IT-GiuseppeMultilingualNeural",
    "en-us": "en-US-AndrewMultilingualNeural",
    "en-gb": "en-GB-RyanNeural",
}
MAX_SPEECH_SOURCE_BYTES = 20 * 1024 * 1024
COPY_CHUNK = 1024 * 1024
KOKORO_VOICES = {
    "it": {"if_sara", "im_nicola"},
    "en-us": {"af_heart", "am_michael"},
    "en-gb": {"af_heart", "am_michael"},
}


def resolved_options(
    voice: Any = "",
    speed: Any = 1.0,
    language: Any = "it",
    provider: Any = None,
) -> tuple[str, str, float, str]:
    """Resolve again at execution, so queued jobs respect the current audio mode."""
    settings = load_settings()["tts"]
    selected = settings["default_provider"] if provider is None else provider
    if not isinstance(selected, str) or selected not in TTS_PROVIDER_INFO:
        raise ValueError("unknown speech provider")
    if not isinstance(language, str) or language not in VOICE_LANGUAGES:
        raise ValueError("unsupported speech language")
    selected_speed = normalized_speed(speed)
    if not isinstance(voice, str):
        raise ValueError("invalid speech voice")
    if settings.get("offline_mode", False):
        selected = "kokoro"
    if selected == "edge-tts":
        if not voice or voice in KOKORO_VOICES[language]:
            voice = DEFAULT_VOICES[language]
        voice, _, _ = normalized_options(voice, selected_speed, language)
    elif selected == "kokoro":
        # Switching mode must not carry an incompatible voice id into Kokoro.
        if (
            not voice
            or voice in VOICE_LANGUAGES[language]
            or provider not in {None, "kokoro", "edge-tts"}
        ):
            default = settings["kokoro"].get(
                "voice_it" if language == "it" else "voice_en"
            )
            voice = (
                default
                if default in KOKORO_VOICES[language]
                else ("if_sara" if language == "it" else "af_heart")
            )
        if voice not in KOKORO_VOICES[language]:
            raise ValueError("voice does not match the selected language")
    elif len(voice) > 240:
        raise ValueError("invalid speech voice")
    return selected, voice, selected_speed, language


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


def normalized_speed(speed: Any) -> float:
    if isinstance(speed, bool):
        raise ValueError("invalid speech speed")
    try:
        selected_speed = float(speed)
    except (TypeError, ValueError) as exc:
        raise ValueError("invalid speech speed") from exc
    if not math.isfinite(selected_speed) or not 0.75 <= selected_speed <= 1.5:
        raise ValueError("speech speed must be between 0.75 and 1.5")
    return selected_speed


def queue_speech_job(
    runner: SpeechQueue,
    store: JobStore,
    source: Path,
    *,
    source_job: str,
    voice: Any = DEFAULT_VOICES["it"],
    speed: Any = 1.0,
    language: Any = "it",
    provider: Any = None,
) -> dict[str, Any]:
    selected_provider, selected_voice, selected_speed, selected_language = (
        resolved_options(voice, speed, language, provider)
    )
    if not source.is_file():
        raise FileNotFoundError("reviewed reading text is missing")
    if source.stat().st_size > MAX_SPEECH_SOURCE_BYTES:
        raise ValueError("reviewed reading text exceeds the speech limit")

    child = runner.submit(
        "edge-tts",
        "reading.txt",
        {
            "voice": selected_voice,
            "speed": selected_speed,
            "language": selected_language,
            "provider": selected_provider,
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
