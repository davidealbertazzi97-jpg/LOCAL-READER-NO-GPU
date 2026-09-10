#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

os.environ.setdefault("FLAGS_use_mkldnn", "0")
os.environ.setdefault("PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK", "True")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def progress(path: Path, value: float, stage: str) -> None:
    write_json(path, {"progress": value, "stage": stage})


def as_dict(result: Any) -> dict[str, Any]:
    value = getattr(result, "json", result)
    if callable(value):
        value = value()
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            return {"text": value}
    return value if isinstance(value, dict) else {}


def page_text(result: Any) -> list[str]:
    payload = as_dict(result)
    texts: list[str] = []

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            for key, nested in value.items():
                if key in {"rec_texts", "texts"} and isinstance(nested, list):
                    texts.extend(
                        str(item).strip() for item in nested if str(item).strip()
                    )
                elif key in {"text", "block_content"} and isinstance(nested, str):
                    if nested.strip():
                        texts.append(nested.strip())
                elif key not in {"rec_boxes", "dt_polys"}:
                    visit(nested)
        elif isinstance(value, list):
            for nested in value:
                visit(nested)

    visit(payload)
    return list(dict.fromkeys(texts))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--progress", required=True)
    args = parser.parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    progress_path = Path(args.progress)
    try:
        from paddleocr import PaddleOCR

        progress(progress_path, 0.04, "Caricamento modelli PaddleOCR")
        try:
            pipeline = PaddleOCR(
                lang="it",
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
                device="cpu",
                enable_mkldnn=False,
                cpu_threads=max(1, min(6, os.cpu_count() or 4)),
            )
        except TypeError:
            pipeline = PaddleOCR(lang="it", use_angle_cls=False)

        page_payload: list[dict[str, Any]] = []
        for page_number, result in enumerate(
            pipeline.predict(input=str(input_path)),
            start=1,
        ):
            texts = page_text(result)
            page_payload.append({"number": page_number, "texts": texts})
            progress(
                progress_path,
                min(0.94, 0.08 + page_number * 0.02),
                f"PaddleOCR: pagina {page_number}",
            )

        text = "\n\n".join("\n".join(page["texts"]) for page in page_payload)
        write_json(
            output_path,
            {
                "text": text,
                "engine": "PaddleOCR",
                "model": "PP-OCRv6",
                "device": "CPU",
                "pages": page_payload,
                "characters": len(text),
            },
        )
        progress(progress_path, 1.0, "PaddleOCR completato")
        return 0
    except Exception as exc:
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
