#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
from collections.abc import Iterator
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", str(max(1, min(4, os.cpu_count() or 2))))
os.environ.setdefault("OMP_WAIT_POLICY", "PASSIVE")

MAX_CHARACTERS = 2_000_000
MAX_CHUNK = 1_200


def chunks(text: str) -> Iterator[str]:
    paragraphs = re.split(r"\n\s*\n+", text)
    pending = ""
    for paragraph in paragraphs:
        paragraph = re.sub(r"[ \t]+", " ", paragraph).strip()
        if not paragraph:
            continue
        sentences = re.split(r"(?<=[.!?;:])\s+", paragraph)
        for sentence in sentences:
            if len(sentence) > MAX_CHUNK:
                pieces = [
                    sentence[index : index + MAX_CHUNK]
                    for index in range(0, len(sentence), MAX_CHUNK)
                ]
            else:
                pieces = [sentence]
            for piece in pieces:
                candidate = f"{pending} {piece}".strip()
                if pending and len(candidate) > MAX_CHUNK:
                    yield pending
                    pending = piece
                else:
                    pending = candidate
        if pending:
            yield pending
            pending = ""


def write_json(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--voices", required=True)
    parser.add_argument(
        "--voice",
        required=True,
        choices=(
            "im_nicola",
            "if_sara",
            "am_michael",
            "af_heart",
            "bm_george",
            "bf_emma",
        ),
    )
    parser.add_argument("--speed", required=True, type=float)
    parser.add_argument(
        "--language",
        required=True,
        choices=("it", "en-us", "en-gb"),
    )
    args = parser.parse_args()
    source = Path(args.input)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    text = source.read_text(encoding="utf-8", errors="strict").strip()
    if not text:
        raise ValueError("reading text is empty")
    if len(text) > MAX_CHARACTERS:
        raise ValueError("reading text exceeds the supported limit")

    import numpy as np
    import soundfile as sf
    from kokoro_onnx import Kokoro

    engine = Kokoro(args.model, args.voices)
    output_path = output / "speech.wav"
    sample_rate = 24_000
    pause = np.zeros(round(sample_rate * 0.24), dtype=np.float32)
    chunk_count = 0
    sample_count = 0
    with sf.SoundFile(
        output_path,
        mode="w",
        samplerate=sample_rate,
        channels=1,
        subtype="PCM_16",
    ) as audio:
        for chunk in chunks(text):
            samples, generated_rate = engine.create(
                chunk,
                voice=args.voice,
                speed=args.speed,
                lang=args.language,
            )
            if generated_rate != sample_rate:
                raise RuntimeError("Kokoro returned an unexpected sample rate")
            audio.write(samples)
            audio.write(pause)
            sample_count += len(samples) + len(pause)
            chunk_count += 1
    report = {
        "engine": "Kokoro ONNX 0.5.0",
        "model_profile": (
            "INT8 CPU" if "int8" in Path(args.model).name.casefold() else "full"
        ),
        "voice": args.voice,
        "language": args.language,
        "speed": args.speed,
        "sample_rate": sample_rate,
        "chunks": chunk_count,
        "duration_seconds": round(sample_count / sample_rate, 3),
    }
    write_json(output / "speech.json", report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
