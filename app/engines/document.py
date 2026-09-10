from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..config import PATHS
from ..documents import document_from_text_pages, write_exports
from ..processes import run_worker
from .base import EngineResult, LocalEngine


class AccessibleDocumentEngine(LocalEngine):
    engine_id = "accessible-document"
    label_en = "OCR and accessible reading"
    label_it = "OCR e lettura accessibile"
    description_en = (
        "Recognize a PDF or image locally, review reading order, and export clean text."
    )
    description_it = (
        "Riconosce PDF o immagini in locale, permette di rivedere l’ordine di "
        "lettura ed esporta testo pulito."
    )
    accepted_extensions = frozenset(
        {".pdf", ".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".bmp"}
    )

    def process(
        self,
        source: Path,
        output_dir: Path,
        options: dict[str, Any],
    ) -> EngineResult:
        if not PATHS.ocr_python.is_file():
            raise RuntimeError("the isolated OCR environment is not installed")
        output_dir.mkdir(parents=True, exist_ok=True)
        command = [
            str(PATHS.ocr_python),
            str(PATHS.app / "workers" / "paddle_worker.py"),
            "--input",
            str(source),
            "--output",
            str(output_dir / "paddle-result.json"),
            "--progress",
            str(output_dir / "paddle-progress.json"),
        ]
        completed = run_worker(
            command,
            cwd=PATHS.app,
            timeout=2 * 60 * 60,
        )
        if completed.returncode:
            raise RuntimeError("isolated OCR worker failed")
        result_path = output_dir / "paddle-result.json"
        if not result_path.is_file():
            raise RuntimeError("OCR worker did not produce its declared output")
        payload = json.loads(result_path.read_text(encoding="utf-8"))
        document_language = str(options.get("document_language", "it"))
        speech_language = str(options.get("speech_language", "it"))
        page_texts = [
            "\n".join(str(text) for text in page.get("texts", []))
            for page in payload.get("pages", [])
            if isinstance(page, dict)
        ]
        document = document_from_text_pages(
            source.stem[:200] or "Document",
            page_texts,
            language=document_language,
            speech_language=speech_language,
        )
        document = write_exports(output_dir, document)
        report = {
            "engine": "PaddleOCR",
            "model": payload.get("model", "PP-OCRv6"),
            "device": "CPU",
            "pages": len(page_texts),
            "characters": int(payload.get("characters", 0)),
            "review_required": True,
        }
        report_path = output_dir / "ocr-report.json"
        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        document_path = output_dir / "document.json"
        artifacts = [
            document_path,
            output_dir / "accessible.html",
            output_dir / "reading.txt",
            report_path,
        ]
        for page in document["pages"]:
            if page["preview"]:
                artifacts.append(output_dir / page["preview"])
        return EngineResult(
            summary={
                "pages": len(document["pages"]),
                "blocks": sum(len(page["blocks"]) for page in document["pages"]),
                "engine": "PaddleOCR PP-OCRv6 / CPU",
            },
            artifacts=tuple(artifacts),
        )


ENGINE = AccessibleDocumentEngine()
