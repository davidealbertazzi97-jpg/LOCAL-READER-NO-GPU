from __future__ import annotations

import asyncio
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

from workers import audio_utils

with mock.patch.dict(sys.modules, {"audio_utils": audio_utils}):
    from workers import speech_worker


class SpeechWorkerTests(unittest.IsolatedAsyncioTestCase):
    async def test_retry_discards_partial_audio(self):
        attempts = 0

        class Communicate:
            def __init__(self, **kwargs):
                pass

            async def stream(self):
                nonlocal attempts
                attempts += 1
                if attempts == 1:
                    yield {"type": "audio", "data": b"partial"}
                    raise ConnectionError("synthetic interruption")
                yield {"type": "audio", "data": b"complete"}

        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "speech.mp3"
            with (
                mock.patch.dict(
                    sys.modules,
                    {"edge_tts": types.SimpleNamespace(Communicate=Communicate)},
                ),
                mock.patch.object(
                    speech_worker.asyncio, "sleep", new_callable=mock.AsyncMock
                ),
            ):
                await speech_worker.synthesize_chunk(
                    "test", output, voice="test", speed=1
                )
            self.assertEqual(output.read_bytes(), b"complete")
            self.assertEqual(attempts, 2)

    async def test_parallel_chunks_keep_order_and_clean_up(self):
        active = 0
        maximum = 0

        async def synthesize(text, destination, **kwargs):
            nonlocal active, maximum
            active += 1
            maximum = max(maximum, active)
            await asyncio.sleep(0.01 if text == "first" else 0)
            destination.write_bytes(text.encode())
            active -= 1

        def combine(parts, output):
            output.write_bytes(b"".join(part.read_bytes() for part in parts))

        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "speech.mp3"
            with (
                mock.patch.object(
                    speech_worker,
                    "text_chunks",
                    return_value=iter(["first", "second", "third"]),
                ),
                mock.patch.object(
                    speech_worker, "synthesize_chunk", side_effect=synthesize
                ),
                mock.patch.object(speech_worker, "combine_audio", side_effect=combine),
            ):
                count = await speech_worker.synthesize(
                    "test", output, voice="test", speed=1
                )
            self.assertEqual(count, 3)
            self.assertEqual(maximum, 2)
            self.assertEqual(output.read_bytes(), b"firstsecondthird")
            self.assertEqual(list(Path(temporary).iterdir()), [output])

    async def test_failed_parallel_batch_cleans_all_parts(self):
        async def synthesize(text, destination, **kwargs):
            destination.write_bytes(b"partial")
            if text == "second":
                raise ConnectionError("synthetic interruption")
            await asyncio.sleep(0.1)

        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "speech.mp3"
            with (
                mock.patch.object(
                    speech_worker, "text_chunks", return_value=iter(["first", "second"])
                ),
                mock.patch.object(
                    speech_worker, "synthesize_chunk", side_effect=synthesize
                ),
                self.assertRaises(ExceptionGroup),
            ):
                await speech_worker.synthesize("test", output, voice="test", speed=1)
            self.assertEqual(list(Path(temporary).iterdir()), [])
