from __future__ import annotations

import base64
import json
import os
import queue
import subprocess
import threading
from contextlib import suppress
from typing import Any

from .config import PATHS
from .engines.speech import verified_kokoro
from .speech_jobs import KOKORO_VOICES

MAX_LIVE_TEXT = 480
MAX_AUDIO_LINE = 12 * 1024 * 1024


def live_options(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        raise ValueError("Live reading options must be an object")
    text = value.get("text")
    voice = value.get("voice", "if_sara")
    language = value.get("language", "it")
    if not isinstance(text, str) or not text.strip() or len(text) > MAX_LIVE_TEXT:
        raise ValueError("Live reading needs a phrase of 1 to 480 characters")
    if not isinstance(language, str) or language not in KOKORO_VOICES:
        raise ValueError("Unsupported live reading language")
    if not isinstance(voice, str) or voice not in KOKORO_VOICES[language]:
        raise ValueError("Voice does not match the live reading language")
    return {"text": text, "voice": voice, "language": language}


class LiveSpeechBusy(RuntimeError):
    pass


class LiveSpeech:
    """One isolated model shared by bounded, short, local requests."""

    def __init__(self) -> None:
        self._serial = threading.Lock()
        self._lifecycle = threading.Lock()
        self._slots = threading.BoundedSemaphore(3)
        self._process: subprocess.Popen[str] | None = None
        self._responses: queue.Queue[str] = queue.Queue(maxsize=1)

    @staticmethod
    def ready() -> bool:
        return all(
            path.is_file()
            for path in (PATHS.tts_python, PATHS.kokoro_model, PATHS.kokoro_voices)
        )

    def close(self) -> None:
        with self._lifecycle:
            process, self._process = self._process, None
            if process is not None:
                if process.poll() is None:
                    process.kill()
                process.wait(timeout=5)
                if process.stdin:
                    process.stdin.close()

    def _start(self) -> queue.Queue[str]:
        with self._lifecycle:
            if self._process is not None and self._process.poll() is None:
                return self._responses
            model, voices = verified_kokoro()
            environment = os.environ.copy()
            environment.update(
                PYTHONPATH=str(PATHS.app / "runtime_guard"),
                PYTHONNOUSERSITE="1",
                HF_HUB_OFFLINE="1",
                TRANSFORMERS_OFFLINE="1",
            )
            process = subprocess.Popen(
                [
                    str(PATHS.tts_python),
                    str(PATHS.app / "workers" / "live_kokoro_worker.py"),
                    "--model",
                    str(model),
                    "--voices",
                    str(voices),
                ],
                cwd=PATHS.app,
                env=environment,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                encoding="utf-8",
            )
            self._process = process
            responses: queue.Queue[str] = queue.Queue(maxsize=1)
            self._responses = responses

            def receive() -> None:
                if process.stdout is None:
                    responses.put("")
                    return
                try:
                    while line := process.stdout.readline(MAX_AUDIO_LINE + 1):
                        responses.put(line if len(line) <= MAX_AUDIO_LINE else "")
                        if len(line) > MAX_AUDIO_LINE:
                            return
                finally:
                    process.stdout.close()
                    # Wake a request waiting on a worker which exited unexpectedly.
                    with suppress(queue.Full):
                        responses.put_nowait("")

            threading.Thread(target=receive, daemon=True).start()
            return responses

    def render(self, value: Any) -> bytes:
        options = live_options(value)
        if not self._slots.acquire(blocking=False):
            raise LiveSpeechBusy("Local voice is busy; try again")
        try:
            with self._serial:
                try:
                    responses = self._start()
                    process = self._process
                    if process is None or process.stdin is None:
                        raise OSError("Local voice worker stopped")
                    process.stdin.write(json.dumps(options, ensure_ascii=True) + "\n")
                    process.stdin.flush()
                    response = json.loads(responses.get(timeout=90))
                    audio = base64.b64decode(response["audio"], validate=True)
                    if not audio.startswith(b"RIFF") or audio[8:12] != b"WAVE":
                        raise ValueError("Invalid local audio")
                    return audio
                except (OSError, ValueError, KeyError, queue.Empty) as exc:
                    self.close()
                    raise RuntimeError("Kokoro live reading is unavailable") from exc
        finally:
            self._slots.release()


LIVE_SPEECH = LiveSpeech()
