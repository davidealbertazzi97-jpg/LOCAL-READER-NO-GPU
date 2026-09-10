#!/usr/bin/env python3
"""Install the optional MLX Fish Audio S2 Pro 8-bit pack on Apple Silicon."""

from __future__ import annotations

import os
import platform
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
ENV_DIR = APP_DIR / ".venv-mac-voice"
MODEL_DIR = APP_DIR / "models" / "fish-local"
MODEL_REPO = "mlx-community/fish-audio-s2-pro-8bit"
MODEL_REVISION = "c8d4481b3f7cbfe64d855c8b7cda7739502fc3ff"


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=APP_DIR, check=True)


def main() -> int:
    if platform.system() != "Darwin" or platform.machine() != "arm64":
        raise SystemExit("Fish Audio locale richiede macOS Apple Silicon.")
    uv = os.environ.get("LOCAL_AI_APP_UV") or "uv"
    run([uv, "venv", str(ENV_DIR), "--python", "3.12"])
    python = ENV_DIR / "bin" / "python"
    run(
        [
            uv,
            "pip",
            "install",
            "--python",
            str(python),
            "-r",
            str(APP_DIR / "requirements-macos-voice.txt"),
        ]
    )
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    code = (
        "from huggingface_hub import snapshot_download; "
        f"snapshot_download({MODEL_REPO!r}, local_dir={str(MODEL_DIR)!r}, "
        f"revision={MODEL_REVISION!r})"
    )
    run([str(python), "-c", code])
    print("Fish Audio S2 Pro 8-bit locale installato.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
