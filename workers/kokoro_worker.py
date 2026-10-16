#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import tempfile
import wave
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from audio_utils import FFMPEG, combine_audio, text_chunks


@contextmanager
def portable_espeak_data() -> Iterator[str]:
    """Keep the bundled data inside eSpeak's fixed native path buffer."""
    import espeakng_loader

    data = Path(espeakng_loader.get_data_path()).resolve()
    # eSpeak NG 1.52 uses 160 bytes on POSIX and 230 on Windows, including NUL.
    limit = 230 if os.name == "nt" else 160
    if len(os.fsencode(data)) < limit:
        yield str(data)
        return
    # macOS's default TMPDIR can itself be long. Resolve /tmp before checking
    # because phonemizer resolves the supplied path before calling eSpeak.
    temporary_root = None if os.name == "nt" else "/tmp"  # nosec B108: private mkdtemp
    with tempfile.TemporaryDirectory(
        prefix="las-tts-", dir=temporary_root
    ) as temporary:
        short_data = Path(temporary).resolve() / "espeak-ng-data"
        if len(os.fsencode(short_data)) >= limit:
            raise RuntimeError("The temporary eSpeak data path is too long")
        shutil.copytree(data, short_data)
        yield str(short_data)


def write_wav(path: Path, samples: object, sample_rate: int) -> None:
    import numpy as np

    values = np.asarray(samples, dtype=np.float32).reshape(-1)
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
    parser.add_argument("--voices", required=True)
    parser.add_argument("--voice", required=True)
    parser.add_argument("--language", choices=("it", "en-us", "en-gb"), default="it")
    parser.add_argument("--speed", type=float, default=1.0)
    args = parser.parse_args()
    source = Path(args.input)
    output = Path(args.output)
    text = source.read_text(encoding="utf-8", errors="strict").strip()
    if not text:
        raise ValueError("reading text is empty")
    try:
        from kokoro_onnx import Kokoro
        from kokoro_onnx.config import EspeakConfig
    except ImportError as exc:
        raise RuntimeError(
            "Kokoro is not installed in the isolated speech environment"
        ) from exc
    import onnxruntime as rt

    session_options = rt.SessionOptions()
    session_options.intra_op_num_threads = max(1, min(4, os.cpu_count() or 2))
    session_options.inter_op_num_threads = 1
    session_options.add_session_config_entry("session.intra_op.allow_spinning", "0")
    session = rt.InferenceSession(
        args.model, sess_options=session_options, providers=["CPUExecutionProvider"]
    )
    output.mkdir(parents=True, exist_ok=True)
    chunks = list(text_chunks(text, maximum=4_000))
    wavs: list[Path] = []
    with portable_espeak_data() as espeak_data:
        engine = Kokoro.from_session(
            session, args.voices, espeak_config=EspeakConfig(data_path=espeak_data)
        )
        for index, chunk in enumerate(chunks):
            samples, sample_rate = engine.create(
                chunk,
                voice=args.voice,
                speed=max(0.75, min(1.5, args.speed)),
                lang="it" if args.language == "it" else "en-us",
            )
            wav = output / f".kokoro-{index:05d}.wav"
            write_wav(wav, samples, sample_rate)
            wavs.append(wav)
    mp3_parts: list[Path] = []
    import subprocess

    if not FFMPEG:
        raise RuntimeError("ffmpeg is required to create MP3 audio")

    for index, wav in enumerate(wavs):
        part = output / f".kokoro-{index:05d}.mp3"
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
                str(part),
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=30 * 60,
        )
        if completed.returncode:
            raise RuntimeError("Kokoro audio conversion failed")
        mp3_parts.append(part)
    combine_audio(mp3_parts, output / "speech.mp3")
    for path in (*wavs, *mp3_parts):
        path.unlink(missing_ok=True)
    (output / "speech.json").write_text(
        json.dumps(
            {
                "engine": "Kokoro 82M ONNX",
                "provider": "kokoro",
                "voice": args.voice,
                "language": args.language,
                "speed": args.speed,
                "format": "mp3",
                "chunks": len(chunks),
                "characters": len(text),
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
