#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import re
from collections.abc import Iterator
from pathlib import Path

MAX_CHARACTERS = 10_000_000
MAX_CHUNK = 2_500
VOICE_CHOICES = (
    "it-IT-GiuseppeMultilingualNeural",
    "it-IT-ElsaNeural",
    "en-US-AndrewMultilingualNeural",
    "en-US-AvaMultilingualNeural",
    "en-GB-RyanNeural",
    "en-GB-SoniaNeural",
)


def chunks(text: str) -> Iterator[str]:
    paragraphs = re.split(r"\n\s*\n+", text)
    pending = ""
    for paragraph in paragraphs:
        paragraph = re.sub(r"[ \t]+", " ", paragraph).strip()
        if not paragraph:
            continue
        sentences = re.split(r"(?<=[.!?;:])\s+", paragraph)
        for sentence in sentences:
            words = sentence.split()
            for word in words:
                candidate = f"{pending} {word}".strip()
                if pending and len(candidate) > MAX_CHUNK:
                    yield pending
                    pending = word
                else:
                    pending = candidate
        if pending:
            yield pending
            pending = ""


def rate_for_speed(speed: float) -> str:
    percentage = round((speed - 1.0) * 100)
    return f"{percentage:+d}%"


async def synthesize(
    text: str,
    output: Path,
    *,
    voice: str,
    speed: float,
) -> int:
    import edge_tts

    count = 0
    rate = rate_for_speed(speed)
    with output.open("wb") as audio:
        for chunk in chunks(text):
            communicate = edge_tts.Communicate(
                text=chunk,
                voice=voice,
                rate=rate,
                volume="+0%",
                pitch="+0Hz",
            )
            async for message in communicate.stream():
                if message["type"] == "audio":
                    audio.write(message["data"])
            count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--voice", required=True, choices=VOICE_CHOICES)
    parser.add_argument("--speed", required=True, type=float)
    parser.add_argument("--language", required=True, choices=("it", "en-us", "en-gb"))
    args = parser.parse_args()
    if not 0.75 <= args.speed <= 1.5:
        raise ValueError("speech speed is outside the supported range")
    source = Path(args.input)
    output_dir = Path(args.output)
    text = source.read_text(encoding="utf-8", errors="strict").strip()
    if not text:
        raise ValueError("reading text is empty")
    if len(text) > MAX_CHARACTERS:
        raise ValueError("reading text exceeds the supported limit")

    output_dir.mkdir(parents=True, exist_ok=True)
    audio = output_dir / "speech.mp3"
    chunk_count = asyncio.run(
        synthesize(text, audio, voice=args.voice, speed=args.speed)
    )
    report = {
        "engine": "Microsoft Edge Neural TTS",
        "provider": "edge-tts",
        "voice": args.voice,
        "language": args.language,
        "speed": args.speed,
        "rate": rate_for_speed(args.speed),
        "format": "mp3",
        "chunks": chunk_count,
        "characters": len(text),
        "network": "Microsoft Edge speech endpoint",
    }
    (output_dir / "speech.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
