#!/usr/bin/env python3
"""Create the pinned Python environment for the generic starter."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
PYTHON_VERSION = "3.12"
SUPPORTED = {
    ("Linux", "x86_64"): "Linux x86-64",
    ("Darwin", "arm64"): "macOS Apple Silicon",
    ("Windows", "AMD64"): "Windows x86-64",
}


def venv_python() -> Path:
    if os.name == "nt":
        return APP_DIR / ".venv" / "Scripts" / "python.exe"
    return APP_DIR / ".venv" / "bin" / "python"


def run(command: list[str]) -> None:
    print(f"\n-> {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=APP_DIR, check=True)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        description="Pinned, cross-platform Local AI App Starter installer."
    )
    root.add_argument(
        "--dry-run",
        action="store_true",
        help="show the platform plan without changing the system",
    )
    return root


def main() -> int:
    args = parser().parse_args()
    system = platform.system()
    machine = platform.machine()
    plan = {
        "platform": SUPPORTED.get((system, machine), f"{system}/{machine}"),
        "officially_tested": (system, machine) in SUPPORTED,
        "python": PYTHON_VERSION,
        "components": ["web-core", "example-engine", "runtime-network-guard"],
    }
    print(json.dumps(plan, indent=2))
    if args.dry_run:
        return 0

    uv = os.environ.get("LOCAL_AI_APP_UV") or shutil.which("uv")
    if not uv:
        raise SystemExit(
            "uv is unavailable. Run install.sh or install.ps1 from the project root."
        )
    python = venv_python()
    if not python.is_file():
        run([uv, "venv", "--python", PYTHON_VERSION, str(APP_DIR / ".venv")])
    run(
        [
            uv,
            "pip",
            "install",
            "--python",
            str(python),
            "--requirement",
            str(APP_DIR / "requirements-core.txt"),
        ]
    )
    run(
        [
            str(python),
            "-c",
            "import fastapi, multipart, uvicorn; print('Starter core ready')",
        ]
    )
    if system == "Linux" and shutil.which("cc"):
        run(["bash", str(APP_DIR / "scripts" / "install-netguard.sh")])
    print("\nInstallation complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
