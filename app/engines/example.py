from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .base import EngineResult, LocalEngine


class TextStatisticsEngine(LocalEngine):
    engine_id = "text-statistics"
    label_en = "Text statistics"
    label_it = "Statistiche del testo"
    description_en = "Example engine: normalize a text file and count its structure."
    description_it = (
        "Motore di esempio: normalizza un file di testo e ne conta la struttura."
    )
    accepted_extensions = frozenset({".txt", ".md", ".csv"})

    def process(
        self,
        source: Path,
        output_dir: Path,
        options: dict[str, Any],
    ) -> EngineResult:
        del options
        text = source.read_text(encoding="utf-8", errors="replace")
        normalized = "\n".join(line.rstrip() for line in text.splitlines()).strip()
        if normalized:
            normalized += "\n"

        output_dir.mkdir(parents=True, exist_ok=True)
        normalized_path = output_dir / "normalized.txt"
        report_path = output_dir / "report.json"
        normalized_path.write_text(normalized, encoding="utf-8")

        report = {
            "characters": len(text),
            "words": len(re.findall(r"\b[\w'-]+\b", text, flags=re.UNICODE)),
            "lines": len(text.splitlines()),
        }
        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return EngineResult(
            summary=report,
            artifacts=(normalized_path, report_path),
        )


ENGINE = TextStatisticsEngine()
