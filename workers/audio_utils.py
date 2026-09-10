#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
import subprocess
from collections.abc import Iterable, Iterator
from pathlib import Path

try:
    from imageio_ffmpeg import get_ffmpeg_exe

    FFMPEG = get_ffmpeg_exe()
except (ImportError, RuntimeError):
    FFMPEG = shutil.which("ffmpeg")


def text_chunks(text: str, maximum: int = 2_000) -> Iterator[str]:
    """Split long text at readable boundaries without dropping characters."""
    paragraphs = re.split(r"\n\s*\n+", text.replace("\r\n", "\n").replace("\r", "\n"))
    pending = ""
    for paragraph in paragraphs:
        paragraph = re.sub(r"[ \t]+", " ", paragraph).strip()
        if not paragraph:
            continue
        for sentence in re.split(r"(?<=[.!?;:])\s+", paragraph):
            words = sentence.split()
            for word in words:
                candidate = f"{pending} {word}".strip()
                if pending and len(candidate) > maximum:
                    yield pending
                    pending = word
                else:
                    pending = candidate
    if pending:
        yield pending


def combine_audio(parts: Iterable[Path], output: Path, *, suffix: str = ".mp3") -> None:
    paths = list(parts)
    if not paths:
        raise RuntimeError("the speech provider returned no audio")
    if len(paths) == 1:
        shutil.copyfile(paths[0], output)
        return
    if not FFMPEG:
        raise RuntimeError("ffmpeg is required to combine long audio")
    listing = output.with_suffix(".concat.txt")

    def concat_line(path: Path) -> str:
        escaped = path.as_posix().replace(
            chr(39), chr(39) + chr(92) + chr(39) + chr(39)
        )
        return f"file '{escaped}'\n"

    listing.write_text(
        "".join(concat_line(path) for path in paths),
        encoding="utf-8",
    )
    try:
        completed = subprocess.run(
            [
                FFMPEG,
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(listing),
                "-c",
                "copy",
                str(output),
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=30 * 60,
        )
        if completed.returncode:
            with output.open("wb") as handle:
                for path in paths:
                    handle.write(path.read_bytes())
    finally:
        listing.unlink(missing_ok=True)
