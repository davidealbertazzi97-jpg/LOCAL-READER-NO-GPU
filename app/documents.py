from __future__ import annotations

import html
import json
import math
import re
from pathlib import Path
from typing import Any

from .utils import atomic_json

ALLOWED_ROLES = {
    "heading1",
    "heading2",
    "heading3",
    "paragraph",
    "list_item",
    "page_number",
    "exclude",
}
BLOCK_ID = re.compile(r"^p[1-9][0-9]{0,3}-b[1-9][0-9]{0,4}$")
MAX_PAGES = 500
MAX_BLOCKS = 20_000
MAX_TEXT = 10_000_000
SPEECH_LANGUAGES = {"it", "en-us", "en-gb"}


def _clean_text(value: Any, *, maximum: int) -> str:
    if not isinstance(value, str):
        raise ValueError("text value must be a string")
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    value = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", value)
    if len(value) > maximum:
        raise ValueError("text value is too long")
    return value.strip()


def validate_document(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("document must be an object")
    title = _clean_text(value.get("title", "Document"), maximum=200) or "Document"
    language = value.get("language", "it")
    if language not in {"it", "en"}:
        raise ValueError("language must be it or en")
    default_speech_language = "it" if language == "it" else "en-us"
    speech_language = value.get("speech_language", default_speech_language)
    if speech_language not in SPEECH_LANGUAGES:
        raise ValueError("invalid speech language")
    if language == "it" and speech_language != "it":
        raise ValueError("Italian documents require an Italian speech language")
    if language == "en" and speech_language not in {"en-us", "en-gb"}:
        raise ValueError("English documents require an English speech language")
    revision = value.get("revision", 1)
    if not isinstance(revision, int) or not 1 <= revision <= 1_000_000:
        raise ValueError("invalid revision")
    raw_pages = value.get("pages")
    if not isinstance(raw_pages, list) or not raw_pages:
        raise ValueError("document must contain at least one page")
    if len(raw_pages) > MAX_PAGES:
        raise ValueError("document contains too many pages")

    pages: list[dict[str, Any]] = []
    total_blocks = 0
    total_text = 0
    seen_ids: set[str] = set()
    for page_index, raw_page in enumerate(raw_pages, start=1):
        if not isinstance(raw_page, dict):
            raise ValueError("page must be an object")
        raw_blocks = raw_page.get("blocks")
        if not isinstance(raw_blocks, list):
            raise ValueError("page blocks must be a list")
        blocks: list[dict[str, Any]] = []
        for block_index, raw_block in enumerate(raw_blocks, start=1):
            if not isinstance(raw_block, dict):
                raise ValueError("block must be an object")
            block_id = raw_block.get("id", f"p{page_index}-b{block_index}")
            if (
                not isinstance(block_id, str)
                or not BLOCK_ID.fullmatch(block_id)
                or block_id in seen_ids
            ):
                raise ValueError("invalid or duplicate block id")
            seen_ids.add(block_id)
            role = raw_block.get("role", "paragraph")
            if role not in ALLOWED_ROLES:
                raise ValueError("invalid block role")
            text = _clean_text(raw_block.get("text", ""), maximum=20_000)
            total_text += len(text)
            confidence = raw_block.get("confidence", 0.0)
            if not isinstance(confidence, (int, float)):
                confidence = 0.0
            confidence = float(confidence)
            if not math.isfinite(confidence):
                raise ValueError("invalid block confidence")
            confidence = max(0.0, min(1.0, confidence))
            raw_bbox = raw_block.get("bbox", [0, 0, 0, 0])
            if (
                not isinstance(raw_bbox, list)
                or len(raw_bbox) != 4
                or not all(isinstance(item, (int, float)) for item in raw_bbox)
                or not all(math.isfinite(float(item)) for item in raw_bbox)
            ):
                raise ValueError("invalid block bounding box")
            blocks.append(
                {
                    "id": block_id,
                    "role": role,
                    "text": text,
                    "confidence": round(confidence, 5),
                    "bbox": [round(float(item), 2) for item in raw_bbox],
                }
            )
        total_blocks += len(blocks)
        page_number = raw_page.get("number", page_index)
        if page_number != page_index:
            raise ValueError("pages must be consecutive")
        preview = raw_page.get("preview", f"pages/page-{page_index:04d}.webp")
        if not isinstance(preview, str) or not re.fullmatch(
            r"pages/page-[0-9]{4}\.webp",
            preview,
        ):
            raise ValueError("invalid page preview")
        pages.append({"number": page_index, "preview": preview, "blocks": blocks})
    if total_blocks > MAX_BLOCKS or total_text > MAX_TEXT:
        raise ValueError("document exceeds the local editing limit")
    return {
        "schema": 1,
        "revision": revision,
        "title": title,
        "language": language,
        "speech_language": speech_language,
        "pages": pages,
    }


def reading_text(document: dict[str, Any]) -> str:
    parts: list[str] = []
    list_prefix = (
        "List item" if document.get("language") == "en" else "Elemento dell’elenco"
    )
    for page in document["pages"]:
        for block in page["blocks"]:
            text = str(block["text"]).strip()
            role = block["role"]
            if not text or role in {"exclude", "page_number"}:
                continue
            if role in {"heading1", "heading2", "heading3"}:
                parts.append(f"\n{text}\n")
            elif role == "list_item":
                cleaned = re.sub(r"^\s*(?:[-•*]|\d+[.)])\s*", "", text)
                parts.append(f"{list_prefix}: {cleaned}")
            else:
                parts.append(text)
    return "\n\n".join(part.strip() for part in parts if part.strip()).strip() + "\n"


def accessible_html(document: dict[str, Any]) -> str:
    body: list[str] = []
    list_open = False
    page_label = "Page" if document.get("language") == "en" else "Pagina"
    for page in document["pages"]:
        body.append(
            f'<section class="page" aria-label="{page_label} {page["number"]}">'
        )
        for block in page["blocks"]:
            text = str(block["text"]).strip()
            role = block["role"]
            if not text or role in {"exclude", "page_number"}:
                continue
            if role == "list_item":
                if not list_open:
                    body.append("<ul>")
                    list_open = True
                cleaned = re.sub(r"^\s*(?:[-•*]|\d+[.)])\s*", "", text)
                body.append(f"<li>{html.escape(cleaned)}</li>")
                continue
            if list_open:
                body.append("</ul>")
                list_open = False
            tag = {
                "heading1": "h1",
                "heading2": "h2",
                "heading3": "h3",
                "paragraph": "p",
            }.get(role, "p")
            body.append(f"<{tag}>{html.escape(text)}</{tag}>")
        if list_open:
            body.append("</ul>")
            list_open = False
        body.append("</section>")
    title = html.escape(str(document["title"]))
    language = html.escape(str(document["language"]))
    return (
        "<!doctype html>\n"
        f'<html lang="{language}">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{title}</title>\n"
        "<style>"
        "body{font:1.15rem/1.65 system-ui,sans-serif;max-width:72ch;"
        "margin:2rem auto;padding:0 1rem;color:#172322;background:#fff}"
        "h1,h2,h3{line-height:1.25}.page{margin:0 0 3rem}"
        "@media(prefers-color-scheme:dark){body{color:#e9f1ef;background:#111}}"
        "</style>\n</head>\n<body>\n" + "\n".join(body) + "\n</body>\n</html>\n"
    )


def write_exports(output_dir: Path, raw_document: Any) -> dict[str, Any]:
    document = validate_document(raw_document)
    output_dir.mkdir(parents=True, exist_ok=True)
    atomic_json(output_dir / "document.json", document)
    _atomic_text(output_dir / "reading.txt", reading_text(document))
    _atomic_text(output_dir / "accessible.html", accessible_html(document))
    return document


def load_document(path: Path) -> dict[str, Any]:
    return validate_document(json.loads(path.read_text(encoding="utf-8")))


def _atomic_text(path: Path, text: str) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)
