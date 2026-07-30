#!/usr/bin/env python3
"""Create the isolated environments for Local Accessibility Studio."""

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


def venv_python(name: str) -> Path:
    if os.name == "nt":
        return APP_DIR / name / "Scripts" / "python.exe"
    return APP_DIR / name / "bin" / "python"


def run(command: list[str]) -> None:
    print(f"\n-> {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=APP_DIR, check=True)


def install_requirements(uv: str, name: str, requirements: str) -> Path:
    python = venv_python(name)
    if not python.is_file():
        run([uv, "venv", "--python", PYTHON_VERSION, str(APP_DIR / name)])
    run(
        [
            uv,
            "pip",
            "install",
            "--python",
            str(python),
            "--requirement",
            str(APP_DIR / requirements),
        ]
    )
    return python


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        description="Pinned Local Accessibility Studio installer."
    )
    root.add_argument(
        "--core-only",
        action="store_true",
        help="install only the web core, for CI and interface development",
    )
    root.add_argument(
        "--skip-models",
        action="store_true",
        help="do not download the verified Kokoro model and voices",
    )
    root.add_argument(
        "--skip-desktop",
        action="store_true",
        help="do not install the Linux desktop launcher",
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
        "components": [
            "web-core",
            *(
                []
                if args.core_only
                else [
                    "rapidocr-ppocrv6-small",
                    "kokoro-onnx-cpu",
                    *([] if args.skip_models else ["kokoro-int8-model"]),
                ]
            ),
            "runtime-network-guard",
        ],
    }
    print(json.dumps(plan, indent=2))
    if args.dry_run:
        return 0

    uv = os.environ.get("LOCAL_AI_APP_UV") or shutil.which("uv")
    if not uv:
        raise SystemExit(
            "uv is unavailable. Run install.sh or install.ps1 from the project root."
        )
    core_python = install_requirements(uv, ".venv", "requirements-core.txt")
    run(
        [
            str(core_python),
            "-c",
            "import fastapi, multipart, uvicorn; print('Web core ready')",
        ]
    )

    if not args.core_only:
        ocr_python = install_requirements(
            uv,
            ".venv-ocr",
            "requirements-ocr.txt",
        )
        run(
            [
                str(ocr_python),
                "-c",
                "import onnxruntime, pypdfium2, rapidocr; print('OCR ready')",
            ]
        )
        tts_python = install_requirements(
            uv,
            ".venv-tts",
            "requirements-tts.txt",
        )
        run(
            [
                str(tts_python),
                "-c",
                "import kokoro_onnx, onnxruntime, soundfile; print('Kokoro ready')",
            ]
        )
        if not args.skip_models:
            run([str(core_python), str(APP_DIR / "scripts" / "install_kokoro.py")])

    if system == "Linux" and shutil.which("cc"):
        run(["bash", str(APP_DIR / "scripts" / "install-netguard.sh")])
    if system == "Linux" and not args.skip_desktop:
        run(["bash", str(APP_DIR / "scripts" / "install-desktop.sh")])
    print("\nLocal Accessibility Studio installation complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
