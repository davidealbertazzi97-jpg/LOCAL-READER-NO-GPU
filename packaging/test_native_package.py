#!/usr/bin/env python3
"""Native CI: install the real embedded payload, then exercise its own runtime."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def diagnose_offline_speech(runtime: Path, environment: dict[str, str]) -> None:
    """Expose the worker failure using synthetic input, never user documents."""
    python = (
        runtime
        / ".venv-tts"
        / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    )
    guarded = {
        **environment,
        "PYTHONPATH": str(runtime / "runtime_guard"),
        "HF_HUB_OFFLINE": "1",
        "TRANSFORMERS_OFFLINE": "1",
    }
    with tempfile.TemporaryDirectory(prefix="native-tts-diagnostic-") as temporary:
        fixture = Path(temporary)
        source = fixture / "reading.txt"
        source.write_text("Questo audio resta sul computer.", encoding="utf-8")
        print("Diagnosing offline speech with synthetic input...", flush=True)
        subprocess.run(
            [
                str(python),
                str(runtime / "workers/kokoro_worker.py"),
                "--input",
                str(source),
                "--output",
                str(fixture / "speech"),
                "--model",
                str(runtime / "models/kokoro/kokoro-v1.0.onnx"),
                "--voices",
                str(runtime / "models/kokoro/voices-v1.0.bin"),
                "--voice",
                "if_sara",
                "--language",
                "it",
            ],
            cwd=runtime,
            env=guarded,
            check=False,
            timeout=120,
        )


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
        try:
            subprocess.run(
                [str(python), str(runtime / "tests/smoke_local.py"), *flags],
                cwd=runtime,
                check=True,
                env=environment,
            )
        except subprocess.CalledProcessError:
            if flags == ["--offline"]:
                diagnose_offline_speech(runtime, environment)
            raise
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
