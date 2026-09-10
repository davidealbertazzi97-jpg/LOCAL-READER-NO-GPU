#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.reflow import (  # noqa: E402
    MAX_REFLOW_BYTES,
    format_for_speech,
    reflow_chunks,
    validated_model_output,
)


def write_json(path: Path, payload: dict[str, object]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def call_model(
    executable: Path,
    model: Path,
    prompt: str,
    device: str,
) -> str:
    gpu_layers = {"cpu": "0", "gpu": "all", "auto": "auto"}[device]
    command = [
        str(executable),
        "--model",
        str(model),
        "--prompt",
        prompt,
        "--predict",
        "2048",
        "--temp",
        "0",
        "--top-k",
        "1",
        "--seed",
        "42",
        "--gpu-layers",
        gpu_layers,
        "--reasoning",
        "off",
        "--reasoning-budget",
        "0",
        "--no-display-prompt",
        "--simple-io",
    ]
    if "completion" in executable.name.casefold():
        command.append("-no-cnv")
    else:
        command.extend(("--no-show-timings", "--log-disable", "--single-turn"))
    completed = subprocess.run(
        command,
        cwd=executable.parent,
        check=False,
        capture_output=True,
        text=True,
        timeout=15 * 60,
    )
    if completed.returncode:
        raise RuntimeError("llama.cpp did not complete the reflow")
    return completed.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--llama-cli", required=True)
    parser.add_argument("--device", choices=("auto", "cpu", "gpu"), default="auto")
    args = parser.parse_args()
    source = Path(args.input)
    output = Path(args.output)
    model = Path(args.model)
    executable = Path(args.llama_cli)
    try:
        text = source.read_text(encoding="utf-8", errors="strict")
        if not text.strip():
            raise ValueError("reading text is empty")
        if len(text.encode("utf-8")) > MAX_REFLOW_BYTES:
            raise ValueError("reading text exceeds the local limit")

        chunks = list(reflow_chunks(text))
        results: list[str] = []
        model_chunks = 0
        fallback_chunks = 0
        for chunk in chunks:
            prompt = (
                "Sei un impaginatore per la sintesi vocale.\n"
                "Riorganizza SOLO gli spazi e i ritorni a capo del testo tra i "
                "marcatori.\n"
                "Non cambiare, correggere, tradurre, riassumere, aggiungere o togliere "
                "alcun carattere diverso dagli spazi bianchi. Non usare Markdown. "
                "Non scrivere spiegazioni. Il ragionamento è disattivato.\n\n"
                "TESTO:\n<<<\n"
                f"{chunk}\n"
                ">>>\n"
                "OUTPUT SOLO IL TESTO IMPAGINATO:\n"
            )
            try:
                candidate = call_model(executable, model, prompt, args.device)
                accepted = validated_model_output(chunk, candidate)
            except (OSError, RuntimeError, subprocess.TimeoutExpired):
                accepted = None
            if accepted is None:
                results.append(format_for_speech(chunk))
                fallback_chunks += 1
            else:
                results.append(accepted)
                model_chunks += 1

        output.mkdir(parents=True, exist_ok=True)
        (output / "reading.txt").write_text(
            "\n\n".join(part.strip() for part in results if part.strip()) + "\n",
            encoding="utf-8",
        )
        write_json(
            output / "reflow-report.json",
            {
                "engine": "llama.cpp",
                "model": model.name,
                "device": args.device,
                "reasoning": "disabled",
                "chunks": len(chunks),
                "model_chunks": model_chunks,
                "fallback_chunks": fallback_chunks,
                "characters": len(text),
                "content_guard": "non-whitespace characters preserved",
            },
        )
        return 0
    except Exception as exc:
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
