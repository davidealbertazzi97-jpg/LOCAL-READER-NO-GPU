from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..documents import document_from_text_pages, write_exports
from .base import EngineResult, LocalEngine

MAX_TEXT_BYTES = 20 * 1024 * 1024


class PlainTextEngine(LocalEngine):
    engine_id = "plain-text"
    label_en = "Pasted or text-file reading"
    label_it = "Testo incollato o da file"
    description_en = "Prepare pasted text or a .txt/.md file for speech."
    description_it = "Prepara testo incollato o un file .txt/.md per la lettura vocale."
    accepted_extensions = frozenset({".txt", ".text", ".md", ".markdown"})

    def process(
        self,
        source: Path,
        output_dir: Path,
        options: dict[str, Any],
    ) -> EngineResult:
        if source.stat().st_size > MAX_TEXT_BYTES:
            raise ValueError("text input exceeds the local limit")
        text = source.read_text(encoding="utf-8", errors="strict")
        if not text.strip():
            raise ValueError("text input is empty")
        language = str(options.get("document_language", "it"))
        speech_language = str(options.get("speech_language", "it"))
        document = document_from_text_pages(
            source.stem[:200] or "Testo incollato",
            [text],
            language=language,
            speech_language=speech_language,
        )
        output_dir.mkdir(parents=True, exist_ok=True)
        document = write_exports(output_dir, document)
        if options.get("preserve_text"):
            # Solo voce deve leggere il testo consegnato dall’utente, senza
            # passare da una normalizzazione editoriale intermedia.
            (output_dir / "reading.txt").write_text(text, encoding="utf-8")
        report = {
            "engine": "Plain text input",
            "source": "paste or text file",
            "characters": len(text),
            "preserved_input": bool(options.get("preserve_text")),
            "review_required": True,
        }
        report_path = output_dir / "text-report.json"
        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return EngineResult(
            summary={"characters": len(text), "engine": "Plain text"},
            artifacts=(
                output_dir / "document.json",
                output_dir / "accessible.html",
                output_dir / "reading.txt",
                report_path,
            ),
        )


ENGINE = PlainTextEngine()
