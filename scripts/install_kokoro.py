#!/usr/bin/env python3
"""Install the verified Kokoro INT8 CPU model and Italian voice bundle."""

from __future__ import annotations

import hashlib
import os
import urllib.parse
import urllib.request
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
TARGET = APP_DIR / "models" / "kokoro"
ASSETS = (
    (
        "kokoro-v1.0.int8.onnx",
        92_361_271,
        "6e742170d309016e5891a994e1ce1559c702a2ccd0075e67ef7157974f6406cb",
    ),
    (
        "voices-v1.0.bin",
        28_214_398,
        "bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d",
    ),
)
BASE_URL = (
    "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def verified(path: Path, expected_size: int, expected_hash: str) -> bool:
    return (
        path.is_file()
        and path.stat().st_size == expected_size
        and digest(path) == expected_hash
    )


def download(name: str, expected_size: int, expected_hash: str) -> None:
    destination = TARGET / name
    if verified(destination, expected_size, expected_hash):
        print(f"Verified existing {name}")
        return
    if destination.exists():
        raise RuntimeError(
            f"{destination} exists but does not match the approved release"
        )
    url = urllib.parse.urljoin(BASE_URL, name)
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname != "github.com":
        raise RuntimeError("unexpected Kokoro download URL")
    temporary = destination.with_suffix(destination.suffix + ".download")
    if temporary.exists():
        temporary.unlink()
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Local-Accessibility-Studio/0.1"},
    )
    try:
        response = urllib.request.urlopen(request, timeout=60)  # nosec B310
        received = 0
        with (
            response,
            temporary.open("xb") as output,
        ):
            while chunk := response.read(1024 * 1024):
                received += len(chunk)
                if received > expected_size:
                    raise RuntimeError(f"download exceeds the approved size for {name}")
                output.write(chunk)
        if received != expected_size:
            raise RuntimeError(f"download size verification failed for {name}")
        if not verified(temporary, expected_size, expected_hash):
            raise RuntimeError(f"checksum verification failed for {name}")
        os.replace(temporary, destination)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    print(f"Installed and verified {name}")


def main() -> int:
    TARGET.mkdir(parents=True, exist_ok=True)
    for asset in ASSETS:
        download(*asset)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
