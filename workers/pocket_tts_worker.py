#!/usr/bin/env python3
"""Generate offline cloned speech with Kyutai Pocket TTS."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from audio_utils import FFMPEG


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--reference-audio", required=True)
    parser.add_argument("--language", default="it")
    parser.add_argument("--speed", type=float, default=1.0)
    args = parser.parse_args()
    source, output, reference = (
        Path(args.input),
        Path(args.output),
        Path(args.reference_audio),
    )
    if not reference.is_file():
        raise RuntimeError("Pocket TTS reference audio is missing")
    text = source.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError("reading text is empty")
    try:
        from pocket_tts import TTSModel
    except ImportError as exc:
        raise RuntimeError("Pocket TTS non è installato nell'ambiente vocale") from exc
    try:
        model = TTSModel.load_model()
        state = model.get_state_for_audio_prompt(str(reference), truncate=True)
    except ValueError as exc:
        raise RuntimeError(
            "Pocket TTS richiede il download del modello voice-cloning gated "
            "da kyutai/pocket-tts e l'accettazione dei termini su Hugging Face"
        ) from exc
    audio = model.generate_audio(state, text)
    output.mkdir(parents=True, exist_ok=True)
    wav = output / ".pocket.wav"
    import scipy.io.wavfile

    scipy.io.wavfile.write(str(wav), model.sample_rate, audio.detach().cpu().numpy())
    mp3 = output / "speech.mp3"
    if not FFMPEG:
        raise RuntimeError("ffmpeg is required to create MP3 audio")
    completed = subprocess.run(
        [
            FFMPEG,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(wav),
            "-codec:a",
            "libmp3lame",
            "-q:a",
            "4",
            str(mp3),
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=1800,
    )
    wav.unlink(missing_ok=True)
    if completed.returncode or not mp3.is_file():
        raise RuntimeError("Pocket TTS audio conversion failed")
    (output / "speech.json").write_text(
        json.dumps(
            {
                "provider": "pocket-tts",
                "engine": "Kyutai Pocket TTS",
                "voice": "cloned",
                "language": args.language,
                "speed": args.speed,
                "network": "offline",
                "voice_cloned": True,
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
