from __future__ import annotations

import hashlib
import importlib.util
import io
import os
import subprocess
import sys
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location(
    "las_launcher", ROOT / "packaging/launcher.py"
)
launcher = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(launcher)


class PortableLauncherTests(unittest.TestCase):
    def test_zip_rejects_paths_links_and_special_files(self):
        for name in (
            "../outside",
            "/outside",
            "C:/outside",
            "C:outside",
            "..\\outside",
        ):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temporary:
                stream = io.BytesIO()
                with zipfile.ZipFile(stream, "w") as archive:
                    archive.writestr(name, "bad")
                stream.seek(0)
                with (
                    zipfile.ZipFile(stream) as archive,
                    self.assertRaises(RuntimeError),
                ):
                    launcher.safe_zip_extract(archive, Path(temporary))

    @unittest.skipIf(os.name == "nt", "POSIX uv tar installation")
    def test_first_run_uv_tar_is_extracted_while_open(self):
        stream = io.BytesIO()
        with tarfile.open(fileobj=stream, mode="w:gz") as archive:
            member = tarfile.TarInfo("uv-platform/uv")
            member.size = 4
            member.mode = 0o755
            archive.addfile(member, io.BytesIO(b"test"))
        content = stream.getvalue()
        with (
            tempfile.TemporaryDirectory() as temporary,
            patch.object(launcher.platform, "system", return_value="Linux"),
            patch.object(launcher.platform, "machine", return_value="x86_64"),
            patch.object(
                launcher,
                "UV_BUILDS",
                {
                    ("Linux", "x86_64"): (
                        "uv.tar.gz",
                        hashlib.sha256(content).hexdigest(),
                    )
                },
            ),
            patch.object(
                launcher.urllib.request, "urlopen", return_value=io.BytesIO(content)
            ),
        ):
            executable = launcher.download_uv(Path(temporary))
            self.assertEqual(executable.read_bytes(), b"test")
            self.assertTrue(os.access(executable, os.X_OK))

    def test_failed_bootstrap_retries_even_with_existing_core(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            core = (
                root
                / ".venv"
                / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            )
            core.parent.mkdir(parents=True)
            core.touch()
            with (
                patch.object(sys, "argv", ["launcher", "--install-only"]),
                patch.object(launcher, "verify_payload", return_value="0.3.3"),
                patch.object(launcher, "platform_root", return_value=root),
                patch.object(launcher, "install_payload", return_value=root),
                patch.object(launcher, "download_uv", return_value=root / "uv"),
                patch.object(
                    launcher,
                    "run",
                    side_effect=subprocess.CalledProcessError(1, "bootstrap"),
                ),
                self.assertRaises(subprocess.CalledProcessError),
            ):
                launcher.main()
            self.assertFalse((root / ".bootstrap-complete").exists())
            with (
                patch.object(sys, "argv", ["launcher", "--install-only"]),
                patch.object(launcher, "verify_payload", return_value="0.3.3"),
                patch.object(launcher, "platform_root", return_value=root),
                patch.object(launcher, "install_payload", return_value=root),
                patch.object(launcher, "download_uv", return_value=root / "uv"),
                patch.object(launcher, "run") as run,
            ):
                self.assertEqual(launcher.main(), 0)
                run.assert_called_once()
                self.assertTrue((root / ".bootstrap-complete").is_file())
                self.assertEqual(launcher.main(), 0)
                run.assert_called_once()

    def test_release_installer_versions_match_product(self):
        import tomllib

        version = tomllib.loads((ROOT / "product.toml").read_text())["product"][
            "version"
        ]
        for name in ("install-release.sh", "install-release.ps1"):
            self.assertIn(f'"{version}"', (ROOT / name).read_text())


if __name__ == "__main__":
    unittest.main()
