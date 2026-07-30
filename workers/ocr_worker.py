#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import os
import re
import statistics
from collections import Counter
from collections.abc import Iterator
from pathlib import Path
from typing import Any

os.environ.setdefault("OMP_NUM_THREADS", str(max(1, min(4, os.cpu_count() or 2))))
os.environ.setdefault("OMP_WAIT_POLICY", "PASSIVE")

MAX_PAGES = 500
MAX_PIXELS = 25_000_000
MAX_DIMENSION = 5_000
LOW_CONFIDENCE = 0.82


def write_json(path: Path, value: Any) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def normalized_key(text: str) -> str:
    return re.sub(r"\W+", " ", text.casefold()).strip()


def prepare_image(image: Any) -> Any:
    from PIL import Image, ImageOps

    if image.width * image.height > MAX_PIXELS:
        raise ValueError("page exceeds the safe pixel limit")
    image = ImageOps.exif_transpose(image)
    if max(image.size) > MAX_DIMENSION:
        image.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.Resampling.LANCZOS)
    return image.convert("RGB")


def input_pages(source: Path) -> Iterator[tuple[int, Any]]:
    from PIL import Image, ImageSequence

    if source.suffix.casefold() == ".pdf":
        import pypdfium2 as pdfium

        document = pdfium.PdfDocument(source)
        try:
            if not 1 <= len(document) <= MAX_PAGES:
                raise ValueError("PDF page count is outside the supported limit")
            for index in range(len(document)):
                page = document[index]
                try:
                    width_points, height_points = page.get_size()
                    if (
                        not math.isfinite(width_points)
                        or not math.isfinite(height_points)
                        or width_points <= 0
                        or height_points <= 0
                    ):
                        raise ValueError("PDF page dimensions are invalid")
                    render_scale = min(
                        150 / 72,
                        MAX_DIMENSION / width_points,
                        MAX_DIMENSION / height_points,
                        math.sqrt(MAX_PIXELS / (width_points * height_points)),
                    )
                    if render_scale <= 0:
                        raise ValueError("PDF page dimensions are invalid")
                    bitmap = page.render(scale=render_scale)
                    try:
                        yield index + 1, prepare_image(bitmap.to_pil())
                    finally:
                        bitmap.close()
                finally:
                    page.close()
        finally:
            document.close()
        return

    Image.MAX_IMAGE_PIXELS = MAX_PIXELS
    with Image.open(source) as image:
        frames = getattr(image, "n_frames", 1)
        if not 1 <= frames <= MAX_PAGES:
            raise ValueError("image frame count is outside the supported limit")
        for index, frame in enumerate(ImageSequence.Iterator(image), start=1):
            if frame.width * frame.height > MAX_PIXELS:
                raise ValueError("page exceeds the safe pixel limit")
            yield index, prepare_image(frame.copy())


def create_engine() -> Any:
    import rapidocr
    from rapidocr import (
        EngineType,
        LangDet,
        LangRec,
        ModelType,
        OCRVersion,
        RapidOCR,
    )

    model_root = Path(rapidocr.__file__).resolve().parent / "models"
    return RapidOCR(
        params={
            # The latest OmegaConf release that ships entirely as wheels does
            # not accept pathlib values. Supplying the verified wheel's model
            # directory as a string also prevents RapidOCR from assigning one.
            "Global.model_root_dir": str(model_root),
            "Det.engine_type": EngineType.ONNXRUNTIME,
            # PP-OCRv6 small is one unified multilingual model. RapidOCR's
            # current resolver exposes that asset through the CH enum value.
            "Det.lang_type": LangDet.CH,
            "Det.model_type": ModelType.SMALL,
            "Det.ocr_version": OCRVersion.PPOCRV6,
            "Rec.engine_type": EngineType.ONNXRUNTIME,
            "Rec.lang_type": LangRec.CH,
            "Rec.model_type": ModelType.SMALL,
            "Rec.ocr_version": OCRVersion.PPOCRV6,
            "Cls.use_cls": False,
        }
    )


def infer_role(
    text: str,
    bbox: list[float],
    *,
    median_height: float,
    page_height: int,
    first: bool,
) -> str:
    height = max(1.0, bbox[3] - bbox[1])
    stripped = text.strip()
    if bbox[1] > page_height * 0.92 and re.fullmatch(
        r"(?:pagina\s*)?\d+", stripped, re.I
    ):
        return "page_number"
    if re.match(r"^(?:[-•*]|\d+[.)])\s+\S", stripped):
        return "list_item"
    letters = "".join(character for character in stripped if character.isalpha())
    uppercase = bool(letters) and letters.isupper()
    if first and len(stripped) <= 140 and (uppercase or height >= median_height * 1.2):
        return "heading1"
    if len(stripped) <= 140 and (uppercase or height >= median_height * 1.35):
        return "heading2"
    return "paragraph"


def recognize_page(engine: Any, image: Any, page_number: int) -> list[dict[str, Any]]:
    import numpy as np

    result = engine(np.asarray(image))
    raw_texts = getattr(result, "txts", None)
    raw_scores = getattr(result, "scores", None)
    raw_boxes = getattr(result, "boxes", None)
    texts = tuple(raw_texts) if raw_texts is not None else ()
    scores = tuple(raw_scores) if raw_scores is not None else ()
    boxes = tuple(raw_boxes) if raw_boxes is not None else ()
    raw: list[tuple[str, float, list[float]]] = []
    for text, score, points in zip(texts, scores, boxes, strict=True):
        clean = re.sub(r"[ \t]+", " ", str(text)).strip()
        if not clean:
            continue
        coordinates = np.asarray(points, dtype=float)
        bbox = [
            float(coordinates[:, 0].min()),
            float(coordinates[:, 1].min()),
            float(coordinates[:, 0].max()),
            float(coordinates[:, 1].max()),
        ]
        raw.append((clean, float(score), bbox))
    heights = [bbox[3] - bbox[1] for _, _, bbox in raw if bbox[3] > bbox[1]]
    median_height = statistics.median(heights) if heights else 1.0
    blocks: list[dict[str, Any]] = []
    for index, (text, confidence, bbox) in enumerate(raw, start=1):
        blocks.append(
            {
                "id": f"p{page_number}-b{index}",
                "role": infer_role(
                    text,
                    bbox,
                    median_height=median_height,
                    page_height=image.height,
                    first=index == 1,
                ),
                "text": text,
                "confidence": round(confidence, 5),
                "bbox": [round(value, 2) for value in bbox],
            }
        )
    return blocks


def mark_repeated_margins(pages: list[dict[str, Any]]) -> None:
    if len(pages) < 3:
        return
    candidates: list[str] = []
    for page in pages:
        blocks = page["blocks"]
        for block in (*blocks[:2], *blocks[-2:]):
            key = normalized_key(block["text"])
            if 2 <= len(key) <= 100:
                candidates.append(key)
    threshold = max(3, round(len(pages) * 0.6))
    repeated = {key for key, count in Counter(candidates).items() if count >= threshold}
    if not repeated:
        return
    for page in pages:
        blocks = page["blocks"]
        for block in (*blocks[:2], *blocks[-2:]):
            if normalized_key(block["text"]) in repeated:
                block["role"] = "exclude"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    source = Path(args.input)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    pages_dir = output / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)

    engine = create_engine()
    pages: list[dict[str, Any]] = []
    confidences: list[float] = []
    for page_number, image in input_pages(source):
        preview = image.copy()
        preview.thumbnail((1_600, 2_200))
        preview_path = pages_dir / f"page-{page_number:04d}.webp"
        preview.save(preview_path, format="WEBP", quality=82, method=4)
        blocks = recognize_page(engine, image, page_number)
        confidences.extend(float(block["confidence"]) for block in blocks)
        pages.append(
            {
                "number": page_number,
                "preview": f"pages/{preview_path.name}",
                "blocks": blocks,
            }
        )
    if not pages:
        raise ValueError("input did not contain a readable page")
    mark_repeated_margins(pages)

    document = {
        "schema": 1,
        "revision": 1,
        "title": source.stem[:200] or "Document",
        "language": "it",
        "pages": pages,
    }
    low_confidence = sum(score < LOW_CONFIDENCE for score in confidences)
    report = {
        "engine": "RapidOCR 3.9.2",
        "model": "PP-OCRv6 small ONNX",
        "device": "CPU",
        "pages": len(pages),
        "blocks": len(confidences),
        "mean_confidence": (
            round(statistics.fmean(confidences), 5) if confidences else 0.0
        ),
        "low_confidence": low_confidence,
        "review_required": True,
    }
    write_json(output / "document.json", document)
    write_json(output / "ocr-report.json", report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
