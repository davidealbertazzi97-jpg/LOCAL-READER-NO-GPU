import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import windows_download


class WindowsDownloadTests(unittest.TestCase):
    def test_uses_schannel_and_stream_size_limit(self):
        payload = b"checksum-pinned test payload"
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "download.bin"

            def powershell_download(command, *, check, env):
                self.assertTrue(check)
                self.assertTrue(command[0].lower().endswith("\\powershell.exe"))
                self.assertEqual(
                    env["LOCAL_READER_DOWNLOAD_URL"],
                    "https://huggingface.co/model/download",
                )
                self.assertEqual(env["LOCAL_READER_DOWNLOAD_MAX_BYTES"], "64")
                self.assertIn("[Net.SecurityProtocolType]::Tls12", command[-1])
                self.assertIn("$response.ContentLength -gt $limit", command[-1])
                Path(env["LOCAL_READER_DOWNLOAD_DESTINATION"]).write_bytes(payload)

            with (
                patch.object(
                    windows_download.platform, "system", return_value="Windows"
                ),
                patch.object(
                    windows_download.subprocess, "run", side_effect=powershell_download
                ) as run,
            ):
                windows_download.download_with_windows_trust(
                    "https://huggingface.co/model/download", destination, 64, 17
                )

            run.assert_called_once()
            self.assertEqual(destination.read_bytes(), payload)
            self.assertEqual(
                hashlib.sha256(destination.read_bytes()).hexdigest(),
                hashlib.sha256(payload).hexdigest(),
            )

    def test_rejects_unapproved_hosts_before_starting_powershell(self):
        with tempfile.TemporaryDirectory() as temporary:
            with (
                patch.object(
                    windows_download.platform, "system", return_value="Windows"
                ),
                patch.object(windows_download.subprocess, "run") as run,
                self.assertRaisesRegex(RuntimeError, "unexpected Windows download URL"),
            ):
                windows_download.download_with_windows_trust(
                    "https://example.invalid/file", Path(temporary) / "file", 100
                )
            run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
