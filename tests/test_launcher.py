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
START_SPEC = importlib.util.spec_from_file_location(
    "las_start", ROOT / "scripts/start.py"
)
start_app = importlib.util.module_from_spec(START_SPEC)
START_SPEC.loader.exec_module(start_app)


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

    def test_windows_uv_download_uses_windows_trust_and_pinned_archive(self):
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, "w") as archive:
            archive.writestr("uv-x86_64-pc-windows-msvc/uv.exe", b"test")
        content = stream.getvalue()
        expected_hash = hashlib.sha256(content).hexdigest()

        def powershell_download(command, *, check, env):
            self.assertEqual(command[0], "powershell.exe")
            self.assertTrue(check)
            self.assertIn("SecurityProtocolType]::Tls12", command[-1])
            self.assertTrue(env["LOCAL_READER_UV_URL"].startswith("https://"))
            Path(env["LOCAL_READER_UV_ARCHIVE"]).write_bytes(content)

        with (
            tempfile.TemporaryDirectory() as temporary,
            patch.object(launcher.platform, "system", return_value="Windows"),
            patch.object(launcher.platform, "machine", return_value="AMD64"),
            patch.object(
                launcher,
                "UV_BUILDS",
                {
                    ("Windows", "AMD64"): (
                        "uv.zip",
                        expected_hash,
                    )
                },
            ),
            patch.object(launcher.subprocess, "run", side_effect=powershell_download),
        ):
            executable = launcher.download_uv(Path(temporary))
            self.assertEqual(executable.name, "uv.exe")
            self.assertEqual(executable.read_bytes(), b"test")

    def test_windows_vc_runtime_is_signature_checked_and_only_installed_if_missing(self):
        with (
            tempfile.TemporaryDirectory() as temporary,
            patch.object(launcher.platform, "system", return_value="Windows"),
            patch.object(launcher, "windows_vc_runtime_installed", return_value=False),
            patch.object(launcher.subprocess, "run") as run,
        ):
            launcher.ensure_windows_vc_runtime(Path(temporary))
            command = run.call_args.args[0]
            self.assertEqual(command[0], "powershell.exe")
            self.assertIn("Get-AuthenticodeSignature", command[-1])
            self.assertIn("Microsoft Corporation", command[-1])
            self.assertIn("-Verb RunAs", command[-1])
            self.assertTrue(
                run.call_args.kwargs["env"]["LOCAL_READER_VC_URL"].startswith(
                    "https://aka.ms/"
                )
            )

        with (
            tempfile.TemporaryDirectory() as temporary,
            patch.object(launcher.platform, "system", return_value="Windows"),
            patch.object(launcher, "windows_vc_runtime_installed", return_value=True),
            patch.object(launcher.subprocess, "run") as run,
        ):
            launcher.ensure_windows_vc_runtime(Path(temporary))
            run.assert_not_called()

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
                patch.object(launcher, "verify_payload", return_value="0.3.4"),
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
                patch.object(launcher, "verify_payload", return_value="0.3.4"),
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

    def test_running_another_version_is_not_treated_as_this_version(self):
        old_health = {
            "app": "local-reader-no-gpu",
            "status": "ok",
            "version": "0.3.3",
        }
        current_health = {**old_health, "version": "0.3.4"}
        with patch.object(start_app, "get_json", return_value=old_health):
            self.assertFalse(start_app.app_is_ready(8765))
        with patch.object(start_app, "get_json", return_value=current_health):
            self.assertTrue(start_app.app_is_ready(8765))

    def test_release_installer_versions_match_product(self):
        import tomllib

        version = tomllib.loads((ROOT / "product.toml").read_text())["product"][
            "version"
        ]
        for name in ("install-release.sh", "install-release.ps1"):
            self.assertIn(f'"{version}"', (ROOT / name).read_text())


if __name__ == "__main__":
    unittest.main()
