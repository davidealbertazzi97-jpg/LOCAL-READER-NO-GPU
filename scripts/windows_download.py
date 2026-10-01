"""Bounded HTTPS downloads through the Windows Schannel trust store."""

from __future__ import annotations

import os
import platform
import subprocess
import urllib.parse
from pathlib import Path, PureWindowsPath

ALLOWED_HOSTS = {"github.com", "huggingface.co"}
USER_AGENT = "Local-Reader-No-GPU/0.3"
POWERSHELL = (
    PureWindowsPath(os.environ.get("SYSTEMROOT", r"C:\Windows"))
    / "System32"
    / "WindowsPowerShell"
    / "v1.0"
    / "powershell.exe"
)


def download_with_windows_trust(
    url: str,
    destination: Path,
    max_bytes: int,
    timeout_seconds: int = 600,
) -> None:
    """Stream a fixed-host HTTPS download using Schannel and an explicit size cap."""
    if platform.system() != "Windows":
        raise RuntimeError("Windows Schannel download requested outside Windows")
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
        raise RuntimeError("unexpected Windows download URL")
    if max_bytes <= 0 or timeout_seconds <= 0:
        raise ValueError("download size and timeout must be positive")

    destination.parent.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    environment.update(
        {
            "LOCAL_READER_DOWNLOAD_URL": url,
            "LOCAL_READER_DOWNLOAD_DESTINATION": str(destination),
            "LOCAL_READER_DOWNLOAD_MAX_BYTES": str(max_bytes),
            "LOCAL_READER_DOWNLOAD_TIMEOUT_MS": str(timeout_seconds * 1000),
            "LOCAL_READER_DOWNLOAD_USER_AGENT": USER_AGENT,
        }
    )
    powershell = r"""$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$request = [Net.HttpWebRequest]::Create($env:LOCAL_READER_DOWNLOAD_URL)
$request.Method = 'GET'
$request.UserAgent = $env:LOCAL_READER_DOWNLOAD_USER_AGENT
$request.Timeout = [int]$env:LOCAL_READER_DOWNLOAD_TIMEOUT_MS
$request.ReadWriteTimeout = 120000
$response = $null
$sourceStream = $null
$destinationStream = $null
$failed = $false
try {
    $response = $request.GetResponse()
    $limit = [long]$env:LOCAL_READER_DOWNLOAD_MAX_BYTES
    if ($response.ContentLength -gt $limit) { throw 'Download exceeds approved size.' }
    $sourceStream = $response.GetResponseStream()
    $destinationStream = [IO.File]::Open(
        $env:LOCAL_READER_DOWNLOAD_DESTINATION,
        [IO.FileMode]::CreateNew,
        [IO.FileAccess]::Write,
        [IO.FileShare]::None
    )
    $buffer = New-Object byte[] 1048576
    [long]$received = 0
    while (($count = $sourceStream.Read($buffer, 0, $buffer.Length)) -gt 0) {
        $received += $count
        if ($received -gt $limit) { throw 'Download exceeds approved size.' }
        $destinationStream.Write($buffer, 0, $count)
    }
    if ($response.ContentLength -ge 0 -and $received -ne $response.ContentLength) {
        throw 'Download ended before the declared content length.'
    }
}
catch {
    [Console]::Error.WriteLine($_.Exception.Message)
    $failed = $true
}
finally {
    if ($destinationStream) { $destinationStream.Dispose() }
    if ($sourceStream) { $sourceStream.Dispose() }
    if ($response) { $response.Dispose() }
}
if ($failed) { exit 1 }
"""
    subprocess.run(
        [
            str(POWERSHELL),
            "-NoLogo",
            "-NoProfile",
            "-NonInteractive",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            powershell,
        ],
        check=True,
        env=environment,
    )
