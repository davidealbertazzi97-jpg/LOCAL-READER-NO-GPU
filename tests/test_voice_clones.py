from __future__ import annotations

import io
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest import mock

from fastapi import HTTPException, UploadFile
from starlette.requests import Request
from starlette.responses import Response

from app import main, provider_config
from app.config import PATHS
from app.speech_jobs import resolved_options


class VoiceCloneTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="voice-tests-")
        self.addCleanup(self.tmp.cleanup)
        self.paths = replace(PATHS, data=Path(self.tmp.name))
        for module in (main, provider_config):
            patch = mock.patch.object(module, "PATHS", self.paths)
            patch.start()
            self.addCleanup(patch.stop)
        self.root = self.paths.data / "voice-clones"
        self.root.mkdir()

    def legacy_settings(self):
        reference = self.root / "reference.wav"
        reference.write_bytes(b"sample to preserve")
        settings = provider_config.load_settings()
        settings["tts"].update(
            default_provider="pocket-tts",
            offline_provider="pocket-tts",
            offline_mode=True,
        )
        settings["tts"]["pocket-tts"] = {"voice_id": "pocket-tts-test"}
        settings["clones"] = [
            {
                "id": "old-clone",
                "name": "Saved voice",
                "provider": "pocket-tts",
                "voice_id": "pocket-tts-test",
                "reference_audio": str(reference),
            }
        ]
        provider_config._write_settings(settings)
        return reference

    def test_retired_settings_migrate_without_losing_private_records(self):
        reference = self.legacy_settings()
        before = provider_config._settings_path().read_bytes()
        settings = provider_config.load_settings()
        self.assertEqual(settings["tts"]["default_provider"], "kokoro")
        self.assertEqual(settings["tts"]["offline_provider"], "kokoro")
        self.assertEqual(settings["clones"][0]["id"], "old-clone")
        self.assertEqual(before, provider_config._settings_path().read_bytes())
        provider_config.save_settings({"tts": {"offline_mode": True}})
        self.assertEqual(
            provider_config.load_settings()["clones"][0]["id"], "old-clone"
        )
        self.assertTrue(reference.is_file())

    def test_retired_provider_absent_from_all_public_menus(self):
        self.legacy_settings()
        settings = provider_config.public_settings()
        self.assertEqual(settings["clones"], [])
        self.assertNotIn("pocket-tts", settings["tts"])
        self.assertNotIn("pocket-tts", provider_config.TTS_PROVIDER_INFO)
        status = main.status()
        self.assertNotIn("pocket-tts", status["providers"]["tts"])
        self.assertEqual(status["speech"]["provider"], "kokoro")
        self.assertNotIn("pocket-tts", main.local_models())
        self.assertFalse(any("pocket-tts" in route.path for route in main.app.routes))

    def test_old_queued_speech_uses_local_kokoro(self):
        self.legacy_settings()
        for language in ("it", "en-us", "en-gb"):
            provider, voice, speed, result_language = resolved_options(
                "pocket-tts-test", 1.2, language, "pocket-tts"
            )
            self.assertEqual(provider, "kokoro")
            self.assertEqual(voice, "if_sara" if language == "it" else "af_heart")
            self.assertEqual((speed, result_language), (1.2, language))
        self.assertEqual(resolved_options("pocket-tts-test")[0], "kokoro")

    def test_new_settings_cannot_select_removed_provider(self):
        with self.assertRaises(ValueError):
            provider_config.save_settings({"tts": {"default_provider": "pocket-tts"}})

    async def test_removed_provider_cannot_create_clones(self):
        with self.assertRaises(HTTPException) as error:
            await main.create_voice_clone(
                provider="pocket-tts",
                name="test",
                consent="true",
                file=UploadFile(filename="test.wav", file=io.BytesIO(b"sample")),
                reference_text="",
            )
        self.assertEqual(error.exception.status_code, 400)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_other_clones_stay_selectable_and_private(self):
        reference = self.root / "fish.wav"
        reference.write_bytes(b"sample")
        local = provider_config.add_clone(
            provider="fish-local",
            name="Local",
            voice_id="local-test",
            reference_audio=str(reference),
        )
        cloud = provider_config.add_clone(
            provider="elevenlabs", name="Cloud", voice_id="cloud-test"
        )
        clones = provider_config.public_settings()["clones"]
        self.assertEqual(len(clones), 2)
        self.assertTrue(all(c["ready"] for c in clones))
        self.assertNotIn("reference_audio", clones[0])
        self.assertTrue(provider_config.remove_clone(local["id"]))
        self.assertTrue(reference.is_file())
        self.assertEqual(
            provider_config.public_settings()["clones"][0]["id"], cloud["id"]
        )
        self.assertIsNone(
            provider_config.private_voice_file(str(PATHS.app / "README.md"))
        )

    def test_missing_local_sample_is_not_ready(self):
        provider_config.add_clone(
            provider="fish-local",
            name="Missing",
            voice_id="missing",
            reference_audio=str(self.root / "missing.wav"),
        )
        self.assertFalse(provider_config.public_settings()["clones"][0]["ready"])

    async def test_browser_recording_and_preview_permissions_preserved(self):
        request = Request(
            {
                "type": "http",
                "method": "GET",
                "path": "/",
                "headers": [],
                "client": ("127.0.0.1", 12345),
                "server": ("127.0.0.1", 8765),
                "scheme": "http",
                "query_string": b"",
            }
        )

        async def next_response(_):
            return Response()

        response = await main.local_security(request, next_response)
        self.assertIn("microphone=(self)", response.headers["Permissions-Policy"])
        self.assertIn(
            "media-src 'self' blob:", response.headers["Content-Security-Policy"]
        )
        self.assertIn(
            "connect-src 'self' https://api.github.com",
            response.headers["Content-Security-Policy"],
        )

    def test_offline_toggle_does_not_restore_retired_provider(self):
        self.legacy_settings()
        provider_config.save_settings({"tts": {"offline_mode": False}})
        self.assertEqual(resolved_options()[0], "edge-tts")
        provider_config.save_settings({"tts": {"offline_mode": True}})
        self.assertEqual(resolved_options()[0], "kokoro")
        self.assertEqual(
            json.loads(provider_config._settings_path().read_text())["clones"][0]["id"],
            "old-clone",
        )
