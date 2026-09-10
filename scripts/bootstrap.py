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
    environment = os.environ.copy()
    for variable in tuple(environment):
        if variable.startswith(("PIP_", "UV_", "PYTHON")):
            environment.pop(variable, None)
    subprocess.run(command, cwd=APP_DIR, env=environment, check=True)


def install_requirements(uv: str, name: str, requirements: str) -> Path:
    python = venv_python(name)
    if not python.is_file():
        run([uv, "venv", "--python", PYTHON_VERSION, str(APP_DIR / name)])
    run(
        [
            uv,
            "pip",
            "sync",
            "--no-config",
            "--default-index",
            "https://pypi.org/simple",
            "--only-binary",
            ":all:",
            "--require-hashes",
            "--python",
            str(python),
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
        help="skip all model downloads; use models already available on the system",
    )
    root.add_argument(
        "--fast-tts",
        action="store_true",
        help=(
            "kept for installer compatibility; the default Kokoro model is "
            "already quantized for CPU"
        ),
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
                    "paddleocr-pp-ocrv6-cpu",
                    "edge-tts-neural-voices",
                    "kokoro-82m-offline-voice",
                    "lfm2.5-230m-local-model-and-llama-cli",
                    "optional-gemma4-and-mac-fish-models-from-advanced-settings",
                ]
            ),
            "runtime-network-guard",
        ],
    }
    print(json.dumps(plan, indent=2))
    if args.dry_run:
        return 0
    if (system, machine) not in SUPPORTED:
        raise SystemExit(
            f"Unsupported installer platform: {system}/{machine}. "
            "Use Linux x86-64, macOS Apple Silicon, or Windows x86-64."
        )

    uv = os.environ.get("LOCAL_AI_APP_UV") or shutil.which("uv")
    if not uv:
        raise SystemExit(
            "uv is unavailable. Run install.sh or install.ps1 from the project root."
        )
    core_python = install_requirements(uv, ".venv", "requirements-core.lock")
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
            "requirements-ocr.lock",
        )
        run(
            [
                str(ocr_python),
                "-c",
                "import paddle, paddleocr; print('PaddleOCR ready')",
            ]
        )
        if not args.skip_models:
            run([str(ocr_python), str(APP_DIR / "scripts" / "prefetch_paddle.py")])
        tts_python = install_requirements(
            uv,
            ".venv-tts",
            "requirements-tts.lock",
        )
        run(
            [
                str(tts_python),
                "-c",
                (
                    "import edge_tts, imageio_ffmpeg, kokoro_onnx; "
                    "print('Edge-TTS, Kokoro and bundled FFmpeg ready')"
                ),
            ]
        )
        if not args.skip_models:
            run([str(tts_python), str(APP_DIR / "scripts" / "install_kokoro.py")])
            run([str(core_python), str(APP_DIR / "scripts" / "install_lfm.py")])

    if system == "Linux" and shutil.which("cc"):
        run(["bash", str(APP_DIR / "scripts" / "install-netguard.sh")])
    if system == "Linux" and not args.skip_desktop:
        run(["bash", str(APP_DIR / "scripts" / "install-desktop.sh")])
    print("\nLocal Accessibility Studio installation complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
