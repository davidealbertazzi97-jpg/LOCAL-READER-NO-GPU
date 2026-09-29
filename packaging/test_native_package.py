#!/usr/bin/env python3
"""Native CI: install the real embedded payload, then exercise its own runtime."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    spec = importlib.util.spec_from_file_location(
        "las_launcher", ROOT / "packaging/launcher.py"
    )
    launcher = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(launcher)
    executable = Path(sys.argv[1]).resolve()
    environment = os.environ.copy()
    environment["APPIMAGE_EXTRACT_AND_RUN"] = "1"
    subprocess.run([str(executable), "--install-only"], check=True, env=environment)
    runtimes = list((launcher.platform_root() / "runtime").iterdir())
    ready = [p for p in runtimes if (p / ".bootstrap-complete").is_file()]
    if len(ready) != 1:
        raise RuntimeError(
            "Run this test on a fresh CI account with one packaged runtime."
        )
    runtime = ready[0]
    python = (
        runtime / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    )
    for flags in (["--offline"], ["--full"]):
        subprocess.run(
            [str(python), str(runtime / "tests/smoke_local.py"), *flags],
            cwd=runtime,
            check=True,
            env=environment,
        )
    for name in ("core", "ocr", "tts"):
        venv = ".venv" if name == "core" else f".venv-{name}"
        python = (
            runtime / venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        )
        subprocess.run(
            [
                str(python),
                str(ROOT / "packaging/collect_licenses.py"),
                "--output",
                str(ROOT / "build" / "installed-licenses" / name),
            ],
            check=True,
        )


if __name__ == "__main__":
    main()
