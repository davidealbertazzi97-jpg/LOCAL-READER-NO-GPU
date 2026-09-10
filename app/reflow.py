from __future__ import annotations

import re
from collections.abc import Iterator

MAX_REFLOW_BYTES = 20 * 1024 * 1024
MAX_REFLOW_CHUNK = 5_000


def canonical_text(value: str) -> str:
    return re.sub(r"\s+", "", value)


def format_for_speech(text: str) -> str:
    """Adjust whitespace only, keeping every non-whitespace character intact."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def reflow_chunks(text: str, maximum: int = MAX_REFLOW_CHUNK) -> Iterator[str]:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n+", text) if part.strip()]
    pending = ""
    for paragraph in paragraphs:
        words = paragraph.split()
        for word in words:
            candidate = f"{pending} {word}".strip()
            if pending and len(candidate) > maximum:
                yield pending
                pending = word
            else:
                pending = candidate
        if pending:
            yield pending
            pending = ""


def validated_model_output(source: str, candidate: str) -> str | None:
    candidate = candidate.replace("[end of text]", "").strip()
    if not candidate or canonical_text(candidate) != canonical_text(source):
        return None
    return format_for_speech(candidate)
