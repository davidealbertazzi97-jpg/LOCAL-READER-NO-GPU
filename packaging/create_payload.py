#!/usr/bin/env python3
"""Create the source payload used by the platform launchers."""

from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def project_files() -> list[Path]:
    git = shutil.which("git")
    if git is not None and (ROOT / ".git").exists():
        result = subprocess.run(
            [git, "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            cwd=ROOT,
            check=True,
            capture_output=True,
        )
        candidates = [ROOT / raw for raw in result.stdout.decode().split("\0") if raw]
    else:
        # The Windows/macOS builders run from the extracted source payload, which
        # intentionally does not contain .git or require git on the target OS.
        candidates = list(ROOT.rglob("*"))

    excluded_directories = {
        ".git",
        ".pytest_cache",
        ".ruff_cache",
        "bin",
        "build",
        "data",
        "dist",
        "models",
        "outputs",
    }
    files: list[Path] = []
    for path in candidates:
        relative_parts = path.relative_to(ROOT).parts
        if any(
            part in excluded_directories or part.startswith(".venv")
            for part in relative_parts
        ):
            continue
        if path.is_file() and not path.name.endswith((".pyc", ".download")):
            files.append(path)
    return sorted(files, key=lambda path: path.relative_to(ROOT).as_posix())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    files = project_files()
    with zipfile.ZipFile(
        output,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for path in files:
            relative = path.relative_to(ROOT).as_posix()
            archive.write(path, relative)
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    print(f"Created {output} ({len(files)} files, sha256={digest})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
