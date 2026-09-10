#!/usr/bin/env python3
"""Run the optional MLX Fish Audio voice clone on Apple Silicon."""

from __future__ import annotations

import argparse
import json
import subprocess
import wave
from pathlib import Path

from audio_utils import FFMPEG, text_chunks


def write_wav(path: Path, audio: object, sample_rate: int) -> None:
    import numpy as np

    values = np.asarray(audio, dtype=np.float32).reshape(-1)
    pcm = (np.clip(values, -1.0, 1.0) * 32767).astype(np.int16).tobytes()
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        handle.writeframes(pcm)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--reference-audio", required=True)
    parser.add_argument("--reference-text", required=True)
    parser.add_argument("--speed", type=float, default=1.0)
    parser.add_argument("--language", default="it")
    args = parser.parse_args()
    text = Path(args.input).read_text(encoding="utf-8").strip()
    if not text or not args.reference_text.strip():
        raise ValueError("text and reference transcript are required")
    try:
        from mlx_audio.tts.utils import load_model
    except ImportError as exc:
        raise RuntimeError("mlx-audio is not installed") from exc
    model = load_model(args.model)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    wavs: list[Path] = []
    rate = None
    for index, chunk in enumerate(text_chunks(text, maximum=2_000)):
        results = list(
            model.generate(
                text=chunk,
                ref_audio=args.reference_audio,
                ref_text=args.reference_text,
                speed=max(0.75, min(1.5, args.speed)),
                chunk_length=200,
            )
        )
        for result in results:
            rate = int(result.sample_rate)
            path = output / f".fish-{index:05d}.wav"
            write_wav(path, result.audio, rate)
            wavs.append(path)
    if not wavs or not rate or not FFMPEG:
        raise RuntimeError("Fish Audio did not produce audio")
    joined = output / ".fish-joined.wav"
    pcm_parts = []
    for path in wavs:
        with wave.open(str(path), "rb") as handle:
            pcm_parts.append(handle.readframes(handle.getnframes()))
    pcm = b"".join(pcm_parts)
    with wave.open(str(joined), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(rate)
        handle.writeframes(pcm)
    completed = subprocess.run(
        [
            FFMPEG,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(joined),
            "-codec:a",
            "libmp3lame",
            "-q:a",
            "4",
            str(output / "speech.mp3"),
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=60 * 60,
    )
    if completed.returncode:
        raise RuntimeError("Fish Audio MP3 conversion failed")
    for path in (*wavs, joined):
        path.unlink(missing_ok=True)
    (output / "speech.json").write_text(
        json.dumps(
            {
                "engine": "Fish Audio S2 Pro MLX 8-bit",
                "provider": "fish-local",
                "language": args.language,
                "speed": args.speed,
                "format": "mp3",
                "network": "offline",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
