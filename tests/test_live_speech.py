from __future__ import annotations

import base64
import io
import subprocess
import sys
import tempfile
import unittest
import wave
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from app.live_speech import LiveSpeech, LiveSpeechBusy, live_options


class LiveSpeechTests(unittest.TestCase):
    def test_phrase_validation_rejects_invalid_types_and_incompatible_voices(self):
        invalid = [
            None,
            [],
            {},
            {"text": " "},
            {"text": "x" * 481},
            {"text": "Ciao", "voice": ["if_sara"]},
            {"text": "Ciao", "language": []},
            {"text": "Ciao", "voice": "am_michael"},
            {"text": "Ciao", "language": "fr"},
        ]
        for value in invalid:
            with self.subTest(value=value), self.assertRaises(ValueError):
                live_options(value)
        self.assertEqual(live_options({"text": "Città 🌍"})["voice"], "if_sara")

    def test_warm_worker_reuse_crash_recovery_and_bounded_requests(self):
        with tempfile.TemporaryDirectory(prefix="las-live-unit-") as directory:
            root = Path(directory)
            (root / "workers").mkdir()
            worker = root / "workers/live_kokoro_worker.py"
            buffer = io.BytesIO()
            with wave.open(buffer, "wb") as audio:
                audio.setnchannels(1)
                audio.setsampwidth(2)
                audio.setframerate(24000)
                audio.writeframes(b"\0\0" * 240)
            encoded = base64.b64encode(buffer.getvalue()).decode()
            worker.write_text(
                "import json,sys\nfor line in sys.stdin:\n"
                " request=json.loads(line)\n"
                " if request['text']=='crash': sys.exit(1)\n"
                f" print(json.dumps({{'audio':{encoded!r}}}),flush=True)\n"
            )
            paths = SimpleNamespace(app=root, tts_python=Path(sys.executable))
            service = LiveSpeech()
            try:
                with (
                    mock.patch("app.live_speech.PATHS", paths),
                    mock.patch(
                        "app.live_speech.verified_kokoro", return_value=(root, root)
                    ),
                    mock.patch(
                        "app.live_speech.subprocess.Popen", wraps=subprocess.Popen
                    ) as spawn,
                ):
                    first = service.render({"text": "Prima frase"})
                    self.assertEqual(first, buffer.getvalue())
                    service.render({"text": "Seconda frase"})
                    self.assertEqual(spawn.call_count, 1, "model stays warm")
                    env = spawn.call_args.kwargs["env"]
                    self.assertEqual(env["HF_HUB_OFFLINE"], "1")
                    self.assertEqual(env["PYTHONPATH"], str(root / "runtime_guard"))
                    with self.assertRaises(RuntimeError):
                        service.render({"text": "crash"})
                    self.assertIsNone(service._process)
                    service.render({"text": "Riparti"})
                    self.assertEqual(spawn.call_count, 2)
                    for _ in range(3):
                        service._slots.acquire()
                    with self.assertRaises(LiveSpeechBusy):
                        service.render({"text": "Coda piena"})
                    for _ in range(3):
                        service._slots.release()
                    self.assertEqual(list(root.iterdir()), [root / "workers"])
            finally:
                process = service._process
                service.close()
                if process:
                    self.assertIsNotNone(process.poll())


if __name__ == "__main__":
    unittest.main()
