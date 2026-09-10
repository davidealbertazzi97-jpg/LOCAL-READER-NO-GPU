#!/usr/bin/env python3
"""Reject machine-specific absolute home paths from the public source tree."""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOME_PATH = re.compile(r"/(?:home|Users)/[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*")
WINDOWS_HOME_PATH = re.compile(r"[A-Za-z]:[\\/]Users[\\/][A-Za-z0-9._-]+")
SKIP = {Path("scripts/check_portability.py")}


def source_files() -> list[Path]:
    git = shutil.which("git")
    if git is None:
        raise RuntimeError("git is required for the portability check")
    result = subprocess.run(
        [git, "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return [
        ROOT / raw
        for raw in result.stdout.decode().split("\0")
        if raw and Path(raw) not in SKIP and (ROOT / raw).is_file()
    ]


def main() -> int:
    findings: list[str] = []
    for path in source_files():
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if HOME_PATH.search(text) or WINDOWS_HOME_PATH.search(text):
            findings.append(str(path.relative_to(ROOT)))
    if findings:
        print("Machine-specific absolute home paths found:", *findings, sep="\n")
        return 1
    print("Portable source paths check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
