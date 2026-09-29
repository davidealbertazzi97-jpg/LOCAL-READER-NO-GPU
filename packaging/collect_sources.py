#!/usr/bin/env python3
"""Attach original source archives and rebuilding instructions to the release."""

from __future__ import annotations

import hashlib
import json
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    manifest = ROOT / "packaging/third_party_sources.json"
    entries = json.loads(manifest.read_text())
    output = ROOT / "dist/Third-party-runtime-sources.zip"
    output.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(output, "w") as archive:
        archive.write(manifest, "sources.json")
        archive.write(ROOT / "packaging/RUNTIME-SOURCE.md", "README.md")
        for entry in entries:
            with urllib.request.urlopen(entry["url"], timeout=120) as response:  # nosec B310
                data = response.read(entry["size"] + 1)
            if (
                len(data) != entry["size"]
                or hashlib.sha256(data).hexdigest() != entry["sha256"]
            ):
                raise RuntimeError(f"Source checksum mismatch: {entry['name']}")
            archive.writestr(entry["name"], data)
            print(f"Included verified source: {entry['name']}")
    print(f"Created {output.name}")


if __name__ == "__main__":
    main()
