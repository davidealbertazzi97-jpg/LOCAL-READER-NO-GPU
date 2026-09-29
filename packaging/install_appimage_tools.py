#!/usr/bin/env python3
"""Fetch checksum-pinned AppImage tooling and runtime; never use floating latest."""

from __future__ import annotations

import hashlib
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = (
    (
        "appimagetool.AppImage",
        "https://github.com/AppImage/appimagetool/releases/download/1.9.1/appimagetool-x86_64.AppImage",
        "ed4ce84f0d9caff66f50bcca6ff6f35aae54ce8135408b3fa33abfc3cb384eb0",
    ),
    (
        "appimage-runtime-x86_64",
        "https://github.com/AppImage/type2-runtime/releases/download/20251108/runtime-x86_64",
        "2fca8b443c92510f1483a883f60061ad09b46b978b2631c807cd873a47ec260d",
    ),
)


def main() -> None:
    (ROOT / "build").mkdir(exist_ok=True)
    for name, url, expected in ASSETS:
        destination = ROOT / "build" / name
        if (
            destination.is_file()
            and hashlib.sha256(destination.read_bytes()).hexdigest() == expected
        ):
            continue
        with urllib.request.urlopen(url, timeout=120) as response:  # nosec B310
            data = response.read(30 * 1024 * 1024 + 1)
        if hashlib.sha256(data).hexdigest() != expected:
            raise RuntimeError(f"Checksum mismatch: {name}")
        destination.write_bytes(data)
        destination.chmod(0o755)
        print(f"Verified {name}")


if __name__ == "__main__":
    main()
