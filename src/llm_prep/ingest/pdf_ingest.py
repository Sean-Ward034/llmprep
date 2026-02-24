"""PDF ingestion (text-first)."""

from __future__ import annotations

from pathlib import Path

import pdfplumber

from llm_prep.chunking import split_paragraphs
from llm_prep.normalize import normalize_text

PARSER_NAME = "pdfplumber"
PARSER_VERSION = "1.0.0"


def ingest_pdf(path: Path, config: dict) -> dict:
    warnings: list[str] = []
    segments: list[dict] = []
    with pdfplumber.open(path) as pdf:
        page_count = len(pdf.pages)
        for page_idx, page in enumerate(pdf.pages, start=1):
            text = normalize_text(page.extract_text() or "")
            if not text:
                continue
            paragraphs = split_paragraphs(text)
            if not paragraphs:
                paragraphs = [text]
            for p_idx, paragraph in enumerate(paragraphs, start=1):
                segments.append(
                    {
                        "text": paragraph,
                        "metadata": {"page": page_idx},
                        "locator": f"pdf:p={page_idx}#segment={p_idx}",
                    }
                )

    if not segments:
        warnings.append(f"OCR not supported in MVP; no extractable text found in {path}")
    return {
        "parser": {"name": PARSER_NAME, "version": PARSER_VERSION},
        "text_segments": segments,
        "tables": [],
        "warnings": warnings,
        "metadata": {"pages": page_count if "page_count" in locals() else 0},
    }

