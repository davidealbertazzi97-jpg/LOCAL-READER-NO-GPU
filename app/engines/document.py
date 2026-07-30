from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from ..config import PATHS
from ..documents import write_exports
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
        del options
        if not PATHS.ocr_python.is_file():
            raise RuntimeError("the isolated OCR environment is not installed")
        output_dir.mkdir(parents=True, exist_ok=True)
        command = [
            str(PATHS.ocr_python),
            str(PATHS.app / "workers" / "ocr_worker.py"),
            "--input",
            str(source),
            "--output",
            str(output_dir),
        ]
        completed = subprocess.run(
            command,
            cwd=PATHS.app,
            check=False,
            capture_output=True,
            text=True,
            timeout=2 * 60 * 60,
        )
        if completed.returncode:
            raise RuntimeError("isolated OCR worker failed")
        document_path = output_dir / "document.json"
        report_path = output_dir / "ocr-report.json"
        if not document_path.is_file() or not report_path.is_file():
            raise RuntimeError("OCR worker did not produce its declared output")
        raw_document = json.loads(document_path.read_text(encoding="utf-8"))
        document = write_exports(output_dir, raw_document)
        report = json.loads(report_path.read_text(encoding="utf-8"))
        artifacts = [
            document_path,
            output_dir / "accessible.html",
            output_dir / "reading.txt",
            report_path,
        ]
        for page in document["pages"]:
            artifacts.append(output_dir / page["preview"])
        return EngineResult(
            summary={
                "pages": len(document["pages"]),
                "blocks": sum(len(page["blocks"]) for page in document["pages"]),
                "low_confidence": int(report.get("low_confidence", 0)),
                "engine": "RapidOCR PP-OCRv6 small / ONNX CPU",
            },
            artifacts=tuple(artifacts),
        )


ENGINE = AccessibleDocumentEngine()
