"""Input ingestion adapters."""

from pathlib import Path

from llm_prep.ingest.csv_ingest import ingest_csv
from llm_prep.ingest.html_ingest import ingest_html
from llm_prep.ingest.pdf_ingest import ingest_pdf
from llm_prep.ingest.text_ingest import ingest_text
from llm_prep.ingest.xlsx_ingest import ingest_xlsx

SUPPORTED_SUFFIXES = {
    ".csv": "csv",
    ".txt": "text",
    ".md": "text",
    ".html": "html",
    ".htm": "html",
    ".pdf": "pdf",
    ".xlsx": "xlsx",
}


def detect_type(path: Path) -> str | None:
    return SUPPORTED_SUFFIXES.get(path.suffix.lower())


def ingest_by_type(path: Path, source_type: str, config: dict) -> dict:
    if source_type == "csv":
        return ingest_csv(path, config)
    if source_type == "text":
        return ingest_text(path, config)
    if source_type == "html":
        return ingest_html(path, config)
    if source_type == "pdf":
        return ingest_pdf(path, config)
    if source_type == "xlsx":
        return ingest_xlsx(path, config)
    raise ValueError(f"Unsupported source type: {source_type}")

