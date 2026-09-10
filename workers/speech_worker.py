#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from audio_utils import combine_audio, text_chunks

MAX_CHARACTERS = 10_000_000
MAX_CHUNK = 1_800
MAX_ATTEMPTS = 2
VOICE_CHOICES = (
    "it-IT-GiuseppeMultilingualNeural",
    "it-IT-ElsaNeural",
    "en-US-AndrewMultilingualNeural",
    "en-US-AvaMultilingualNeural",
    "en-GB-RyanNeural",
    "en-GB-SoniaNeural",
)


def rate_for_speed(speed: float) -> str:
    percentage = round((speed - 1.0) * 100)
    return f"{percentage:+d}%"


async def synthesize_chunk(
    text: str,
    destination: Path,
    *,
    voice: str,
    speed: float,
) -> None:
    import edge_tts

    rate = rate_for_speed(speed)
    last_error: Exception | None = None
    for attempt in range(MAX_ATTEMPTS):
        destination.unlink(missing_ok=True)
        received = 0
        try:
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice,
                rate=rate,
                volume="+0%",
                pitch="+0Hz",
                connect_timeout=5,
                receive_timeout=20,
            )
            # Keep an active long chunk alive; stalled receives still stop at 20s.
            async with asyncio.timeout(180):
                with destination.open("xb") as audio:
                    async for message in communicate.stream():
                        if message["type"] == "audio":
                            payload = message["data"]
                            audio.write(payload)
                            received += len(payload)
            if received:
                return
            raise RuntimeError("Edge-TTS returned no audio")
        except Exception as exc:
            last_error = exc
            destination.unlink(missing_ok=True)
            if attempt + 1 < MAX_ATTEMPTS:
                await asyncio.sleep(1)
    raise RuntimeError(f"Edge-TTS failed after {MAX_ATTEMPTS} attempts") from last_error


async def synthesize(
    text: str,
    output: Path,
    *,
    voice: str,
    speed: float,
) -> int:
    parts: list[Path] = []
    semaphore = asyncio.Semaphore(2)

    async def generate(chunk: str, part: Path) -> None:
        async with semaphore:
            await synthesize_chunk(chunk, part, voice=voice, speed=speed)

    try:
        # Bounded batches avoid scheduling thousands of tasks for long books.
        chunks = iter(text_chunks(text, maximum=MAX_CHUNK))
        while True:
            batch = []
            for _ in range(2):
                chunk = next(chunks, None)
                if chunk is None:
                    break
                part = output.parent / f".edge-{len(parts):05d}.mp3"
                parts.append(part)
                batch.append((chunk, part))
            if not batch:
                break
            async with asyncio.TaskGroup() as group:
                for chunk, part in batch:
                    group.create_task(generate(chunk, part))
        combine_audio(parts, output)
        return len(parts)
    finally:
        for part in parts:
            part.unlink(missing_ok=True)


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
