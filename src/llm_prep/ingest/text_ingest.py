"""Plain-text ingestion."""

from __future__ import annotations

from pathlib import Path

from llm_prep.chunking import split_paragraphs
from llm_prep.normalize import normalize_text

PARSER_NAME = "text_ingest"
PARSER_VERSION = "1.0.0"


def ingest_text(path: Path, config: dict) -> dict:
    warnings: list[str] = []
    try:
        raw = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raw = path.read_text(encoding="utf-8", errors="ignore")
        warnings.append(f"Decode fallback applied for {path}")

    cleaned = normalize_text(raw)
    segments = []
    for idx, paragraph in enumerate(split_paragraphs(cleaned), start=1):
        segments.append(
            {
                "text": paragraph,
                "metadata": {},
                "locator": f"text:paragraph#{idx}",
            }
        )
    if not segments and cleaned:
        segments.append({"text": cleaned, "metadata": {}, "locator": "text:full"})
    return {
        "parser": {"name": PARSER_NAME, "version": PARSER_VERSION},
        "text_segments": segments,
        "tables": [],
        "warnings": warnings,
    }

