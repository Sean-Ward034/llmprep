"""HTML ingestion."""

from __future__ import annotations

from pathlib import Path

from bs4 import BeautifulSoup

from llm_prep.chunking import split_paragraphs
from llm_prep.extract.tables import infer_schema
from llm_prep.normalize import normalize_text

PARSER_NAME = "html_ingest"
PARSER_VERSION = "1.0.0"


def _visible_text(soup: BeautifulSoup) -> str:
    for tag in soup(["script", "style", "noscript"]):
        tag.extract()
    return "\n".join(part.strip() for part in soup.stripped_strings if part.strip())


def _extract_tables(soup: BeautifulSoup) -> list[dict]:
    tables: list[dict] = []
    for idx, table in enumerate(soup.find_all("table"), start=1):
        rows: list[list[str]] = []
        for tr in table.find_all("tr"):
            row = [cell.get_text(separator=" ", strip=True) for cell in tr.find_all(["th", "td"])]
            if row:
                rows.append(row)
        if not rows:
            continue
        headers = [h or f"column_{i+1}" for i, h in enumerate(rows[0])]
        data_rows = rows[1:] if len(rows) > 1 else []
        schema = infer_schema(headers, data_rows[:50])
        tables.append(
            {
                "table_kind": "html_table",
                "headers": headers,
                "rows": data_rows,
                "schema": schema.model_dump(),
                "metadata": {"html_table_index": idx},
                "locator": f"html:table#{idx}",
            }
        )
    return tables


def ingest_html(path: Path, config: dict) -> dict:
    warnings: list[str] = []
    try:
        html = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        html = path.read_text(encoding="utf-8", errors="ignore")
        warnings.append(f"Decode fallback applied for {path}")

    soup = BeautifulSoup(html, "lxml")
    normalized = normalize_text(_visible_text(soup))
    segments = [
        {
            "text": paragraph,
            "metadata": {},
            "locator": f"html:text#{idx}",
        }
        for idx, paragraph in enumerate(split_paragraphs(normalized), start=1)
    ]
    tables = _extract_tables(soup)
    return {
        "parser": {"name": PARSER_NAME, "version": PARSER_VERSION},
        "text_segments": segments,
        "tables": tables,
        "warnings": warnings,
    }

