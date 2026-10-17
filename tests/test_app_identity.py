from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest import mock

from app import config
from app.product import PRODUCT
from app.security import TOKEN_COOKIE
from scripts import start

ROOT = Path(__file__).resolve().parents[1]


class AppIdentityTests(unittest.TestCase):
    def test_legacy_and_reader_have_separate_data_results_config_and_cookies(self):
        with (
            tempfile.TemporaryDirectory() as directory,
            mock.patch.dict(
                "os.environ",
                {
                    "XDG_DATA_HOME": directory,
                    "XDG_STATE_HOME": directory,
                    "XDG_CONFIG_HOME": directory,
                },
            ),
        ):
            current = config._platform_roots()
            current_config = start.config_root()
            for name, slug in (
                ("Local Accessibility Studio", "local-accessibility-studio"),
                ("Local Reader No GPU", "local-reader-no-gpu"),
            ):
                legacy = replace(PRODUCT, name=name, slug=slug)
                with mock.patch.object(config, "PRODUCT", legacy):
                    previous = config._platform_roots()
                with mock.patch.object(start, "PRODUCT", legacy):
                    previous_config = start.config_root()
                self.assertTrue(set(current).isdisjoint(previous))
                self.assertNotEqual(current_config, previous_config)
                self.assertNotEqual(TOKEN_COOKIE, slug.replace("-", "_") + "_token")
            self.assertEqual(start.DEFAULT_PORT, 8766)

    def test_native_launcher_identity_matches_app_and_explorer_metadata(self):
        spec = importlib.util.spec_from_file_location(
            "reader_launcher", ROOT / "packaging/launcher.py"
        )
        launcher = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(launcher)
        self.assertEqual(launcher.APP_NAME, PRODUCT.name)
        self.assertEqual(launcher.APP_SLUG, PRODUCT.slug)
        self.assertEqual(launcher.WINDOWS_APP_ID, "AiSwarmSolutions.LocalReader")
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "version.txt"
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "packaging/windows_version.py"),
                    str(target),
                ],
                check=True,
            )
            resource = target.read_text()
            self.assertIn("'ProductName', 'Local Reader'", resource)
            self.assertIn("'OriginalFilename', 'local-reader.exe'", resource)
            self.assertNotIn("Local Accessibility Studio", resource)
