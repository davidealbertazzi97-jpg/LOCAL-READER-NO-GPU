from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from ..config import PATHS
from ..processes import run_worker
from ..provider_config import ai_config_for, load_settings
from .base import EngineResult, LocalEngine


class LfmReflowEngine(LocalEngine):
    engine_id = "lfm-reflow"
    label_en = "LFM2.5 230M reading layout"
    label_it = "Impaginazione lettura LFM2.5 230M"
    description_en = "Preserve the text and improve spacing for speech."
    description_it = "Conserva il testo e migliora spazi e capoversi per la voce."
    accepted_extensions = frozenset({".txt"})
    user_upload = False

    def process(
        self,
        source: Path,
        output_dir: Path,
        options: dict[str, Any],
    ) -> EngineResult:
        provider = str(options.get("provider", "local"))
        if load_settings()["tts"].get("offline_mode"):
            provider = "local"
        if provider != "local":
            configured = ai_config_for(provider)
            fd, config_name = tempfile.mkstemp(
                prefix=".reflow-provider-", suffix=".json", dir=PATHS.data
            )
            config_path = Path(config_name)
            try:
                if os.name != "nt":
                    os.chmod(config_path, 0o600)
                with os.fdopen(fd, "w", encoding="utf-8") as handle:
                    json.dump(configured, handle, ensure_ascii=False)
                command = [
                    str(PATHS.tts_python),
                    str(PATHS.app / "workers" / "external_reflow_worker.py"),
                    "--input",
                    str(source),
                    "--output",
                    str(output_dir),
                    "--config",
                    str(config_path),
                ]
                environment = os.environ.copy()
                environment.pop("PYTHONPATH", None)
                environment.pop("LD_PRELOAD", None)
                environment["PYTHONNOUSERSITE"] = "1"
                completed = run_worker(
                    command,
                    cwd=PATHS.app,
                    timeout=12 * 60 * 60,
                    env=environment,
                    network=True,
                )
            finally:
                config_path.unlink(missing_ok=True)
            if completed.returncode:
                raise RuntimeError("external organization provider failed")
            report_path = output_dir / "reflow-report.json"
            text_path = output_dir / "reading.txt"
            if not text_path.is_file() or not report_path.is_file():
                raise RuntimeError(
                    "external organization worker did not produce its output"
                )
            report = json.loads(report_path.read_text(encoding="utf-8"))
            return EngineResult(
                summary={
                    "engine": "OpenAI-compatible organization provider",
                    "provider": provider,
                    "model": report.get("model", configured.get("model", "")),
                    "fallback_chunks": report.get("fallback_chunks", 0),
                },
                artifacts=(text_path, report_path),
            )
        local_model = load_settings()["ai"].get("local_model", "lfm")
        model = PATHS.gemma_model if local_model == "gemma4" else PATHS.llama_model
        if not PATHS.llama_cli.is_file() or not model.is_file():
            label = "Gemma 4" if local_model == "gemma4" else "LFM2.5"
            raise RuntimeError(f"llama.cpp and the {label} model are not installed")
        output_dir.mkdir(parents=True, exist_ok=True)
        command = [
            str(PATHS.tts_python),
            str(PATHS.app / "workers" / "reflow_worker.py"),
            "--input",
            str(source),
            "--output",
            str(output_dir),
            "--model",
            str(model),
            "--llama-cli",
            str(PATHS.llama_cli),
            "--device",
            str(options.get("device", "auto")),
        ]
        completed = run_worker(command, cwd=PATHS.app, timeout=12 * 60 * 60)
        if completed.returncode:
            raise RuntimeError("llama.cpp reflow worker failed")
        report_path = output_dir / "reflow-report.json"
        text_path = output_dir / "reading.txt"
        if not text_path.is_file() or not report_path.is_file():
            raise RuntimeError("reflow worker did not produce its declared output")
        report = json.loads(report_path.read_text(encoding="utf-8"))
        return EngineResult(
            summary={
                "engine": (
                    "Gemma 4 E4B Q4_0 / llama.cpp"
                    if local_model == "gemma4"
                    else "LFM2.5 230M / llama.cpp"
                ),
                "device": report.get("device", "auto"),
                "reasoning": "off",
                "fallback_chunks": report.get("fallback_chunks", 0),
            },
            artifacts=(text_path, report_path),
        )


ENGINE = LfmReflowEngine()
