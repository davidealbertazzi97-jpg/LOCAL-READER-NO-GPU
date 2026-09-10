#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from audio_utils import combine_audio, text_chunks


def request_bytes(
    url: str, headers: dict[str, str], payload: dict[str, object]
) -> bytes:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={**headers, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=10 * 60) as response:  # nosec B310
            body = response.read()
            content_type = response.headers.get("content-type", "")
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"provider request failed with status {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError("provider request could not be completed") from exc
    if "json" not in content_type.casefold():
        return body
    try:
        data = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("provider returned an invalid audio response") from exc
    for key in ("audio_data", "audio", "data", "audio_base64"):
        value = data.get(key) if isinstance(data, dict) else None
        if isinstance(value, str):
            try:
                return base64.b64decode(value, validate=True)
            except ValueError as exc:
                raise RuntimeError("provider returned invalid audio data") from exc
    raise RuntimeError("provider returned no audio data")


def synthesize(
    provider: str, config: dict[str, object], text: str, output: Path, speed: float
) -> int:
    key = str(config.get("api_key", ""))
    model = str(config.get("model", ""))
    voice_id = str(config.get("voice_id", ""))
    if not key:
        raise RuntimeError("the selected provider has no API key configured")
    output.mkdir(parents=True, exist_ok=True)
    parts: list[Path] = []
    maximum = 1_600 if provider == "voxtral" else 2_200
    for index, chunk in enumerate(text_chunks(text, maximum=maximum)):
        if provider == "elevenlabs":
            if not voice_id:
                raise RuntimeError("ElevenLabs needs a voice ID in Settings")
            url = (
                "https://api.elevenlabs.io/v1/text-to-speech/"
                + urllib.parse.quote(voice_id, safe="")
                + "?output_format=mp3_44100_128"
            )
            payload = {
                "text": chunk,
                "model_id": model or "eleven_multilingual_v2",
                "voice_settings": {"speed": max(0.7, min(1.2, speed))},
            }
            audio = request_bytes(url, {"xi-api-key": key}, payload)
        elif provider == "fish":
            url = "https://api.fish.audio/v1/tts"
            payload: dict[str, object] = {
                "text": chunk,
                "format": "mp3",
                "prosody": {"speed": speed},
            }
            if voice_id:
                payload["reference_id"] = voice_id
            audio = request_bytes(
                url,
                {"Authorization": f"Bearer {key}", "model": model or "s2.1"},
                payload,
            )
        elif provider == "voxtral":
            url = "https://api.mistral.ai/v1/audio/speech"
            payload = {
                "model": model or "voxtral-mini-tts-2603",
                "input": chunk,
                "response_format": "mp3",
            }
            if voice_id:
                payload["voice_id"] = voice_id
            audio = request_bytes(url, {"Authorization": f"Bearer {key}"}, payload)
        else:
            raise RuntimeError("unknown cloud speech provider")
        if not audio:
            raise RuntimeError("provider returned an empty audio file")
        part = output / f".cloud-{index:05d}.mp3"
        part.write_bytes(audio)
        parts.append(part)
    combine_audio(parts, output / "speech.mp3")
    for part in parts:
        part.unlink(missing_ok=True)
    (output / "speech.json").write_text(
        json.dumps(
            {
                "engine": provider,
                "provider": provider,
                "model": model,
                "voice": voice_id or "default",
                "speed": speed,
                "format": "mp3",
                "chunks": len(parts),
                "characters": len(text),
                "network": "external provider",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return len(parts)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    try:
        config = json.loads(Path(args.config).read_text(encoding="utf-8"))
        source = Path(args.input)
        text = source.read_text(encoding="utf-8", errors="strict").strip()
        if not text:
            raise ValueError("reading text is empty")
        synthesize(
            str(config.get("provider", "")),
            config,
            text,
            Path(args.output),
            float(config.get("speed", 1.0)),
        )
        return 0
    except Exception as exc:
        print(f"{type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
