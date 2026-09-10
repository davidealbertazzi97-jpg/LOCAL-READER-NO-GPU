from __future__ import annotations

import io
import os
import subprocess
import sys
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent


class RuntimeArchiveTests(unittest.TestCase):
    def test_runtime_library_symlink_is_extracted_safely(self):
        from scripts.install_lfm import safe_members

        stream = io.BytesIO()
        with tarfile.open(fileobj=stream, mode="w") as archive:
            library = tarfile.TarInfo("bin/libggml.so.1")
            library.size = 4
            archive.addfile(library, io.BytesIO(b"test"))
            link = tarfile.TarInfo("bin/libggml.so")
            link.type = tarfile.SYMTYPE
            link.linkname = "libggml.so.1"
            archive.addfile(link)
        stream.seek(0)
        with (
            tempfile.TemporaryDirectory() as temporary,
            tarfile.open(fileobj=stream) as archive,
        ):
            safe_members(archive)
            archive.extractall(temporary, filter="data")
            self.assertEqual((Path(temporary) / "bin/libggml.so").read_bytes(), b"test")

    def test_escaping_runtime_links_are_rejected(self):
        from scripts.install_lfm import safe_members

        for target in ("../../outside", "/etc/passwd", "C:/outside"):
            stream = io.BytesIO()
            with tarfile.open(fileobj=stream, mode="w") as archive:
                link = tarfile.TarInfo("bin/link")
                link.type = tarfile.SYMTYPE
                link.linkname = target
                archive.addfile(link)
            stream.seek(0)
            with (
                tarfile.open(fileobj=stream) as archive,
                self.assertRaises(RuntimeError),
            ):
                safe_members(archive)

    def test_windows_runtime_zip_uses_filename(self):
        from scripts.install_lfm import safe_members

        stream = io.BytesIO()
        with zipfile.ZipFile(stream, "w") as archive:
            archive.writestr("llama-cli.exe", b"test")
        stream.seek(0)
        with zipfile.ZipFile(stream) as archive:
            self.assertEqual(len(safe_members(archive)), 1)


class RuntimeNetworkGuardTests(unittest.TestCase):
    def run_guarded(self, code: str) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(APP_DIR / "runtime_guard")
        environment.pop("LD_PRELOAD", None)
        return subprocess.run(
            [sys.executable, "-c", code],
            cwd=APP_DIR,
            env=environment,
            check=False,
            text=True,
            capture_output=True,
        )

    def test_external_name_resolution_is_denied(self) -> None:
        result = self.run_guarded(
            "import socket\n"
            "try:\n"
            " socket.getaddrinfo('example.com', 443)\n"
            "except socket.gaierror:\n"
            " raise SystemExit(0)\n"
            "raise SystemExit(3)\n"
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_numeric_loopback_is_allowed(self) -> None:
        result = self.run_guarded(
            "import socket\n"
            "value=socket.getaddrinfo('127.0.0.1', 8765)\n"
            "raise SystemExit(0 if value else 4)\n"
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_external_udp_destination_is_denied(self) -> None:
        result = self.run_guarded(
            "import socket\n"
            "sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)\n"
            "try:\n"
            " sock.sendto(b'x', ('192.0.2.1', 9))\n"
            "except PermissionError:\n"
            " raise SystemExit(0)\n"
            "raise SystemExit(5)\n"
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_wildcard_listener_is_denied(self) -> None:
        result = self.run_guarded(
            "import socket\n"
            "sock=socket.socket()\n"
            "try:\n"
            " sock.bind(('0.0.0.0', 0))\n"
            "except PermissionError:\n"
            " raise SystemExit(0)\n"
            "raise SystemExit(6)\n"
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
