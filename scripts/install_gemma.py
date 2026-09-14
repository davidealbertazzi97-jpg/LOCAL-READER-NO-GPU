#!/usr/bin/env python3
"""Download the optional Google Gemma 4 E4B Q4_0 GGUF with a fixed checksum."""

from __future__ import annotations

import hashlib
import os
import urllib.parse
import urllib.request
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
TARGET = APP_DIR / "models" / "gemma4"
NAME = "gemma-4-E4B_q4_0-it.gguf"
SIZE = 5_154_941_280
SHA256 = "676c35070db6dbe52f93e9c864ee0fba4eddea94b9c875d9cb10daff453fbaee"
URL = "https://huggingface.co/google/gemma-4-E4B-it-qat-q4_0-gguf/resolve/main/" + NAME


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def verified(path: Path) -> bool:
    return path.is_file() and path.stat().st_size == SIZE and digest(path) == SHA256


def main() -> int:
    TARGET.mkdir(parents=True, exist_ok=True)
    destination = TARGET / NAME
    if verified(destination):
        print(f"Verified existing {NAME}")
        return 0
    if destination.exists():
        raise RuntimeError(f"{destination} exists but is not the approved model")
    parsed = urllib.parse.urlsplit(URL)
    if parsed.scheme != "https" or parsed.hostname != "huggingface.co":
        raise RuntimeError("unexpected Gemma download URL")
    temporary = destination.with_suffix(destination.suffix + ".download")
    temporary.unlink(missing_ok=True)
    request = urllib.request.Request(
        URL, headers={"User-Agent": "Local-Reader-No-GPU/0.3"}
    )
    try:
        # The host, URL, expected size and SHA-256 are fixed above.
        # nosemgrep
        response = urllib.request.urlopen(request, timeout=120)  # nosec B310
        received = 0
        with response, temporary.open("xb") as output:
            while chunk := response.read(1024 * 1024):
                received += len(chunk)
                if received > SIZE:
                    raise RuntimeError("Gemma download exceeds the approved size")
                output.write(chunk)
        if received != SIZE or not verified(temporary):
            raise RuntimeError("Gemma checksum verification failed")
        os.replace(temporary, destination)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    print(f"Installed and verified {NAME}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
