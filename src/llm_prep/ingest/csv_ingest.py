"""CSV ingestion."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from llm_prep.extract.tables import infer_schema

PARSER_NAME = "csv_ingest"
PARSER_VERSION = "1.0.0"


def _sniff_dialect(sample: str) -> csv.Dialect:
    try:
        return csv.Sniffer().sniff(sample)
    except csv.Error:
        return csv.get_dialect("excel")


def _normalize_rows(rows: list[list[str]]) -> list[list[Any]]:
    normalized: list[list[Any]] = []
    for row in rows:
        normalized.append([cell.strip() for cell in row])
    return normalized


def ingest_csv(path: Path, config: dict) -> dict:
    warnings: list[str] = []
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("utf-8", errors="ignore")
        warnings.append(f"Decode fallback applied for {path}")

    sample_rows = int(config.get("csv_sample_rows", 50))
    lines = text.splitlines()
    sample = "\n".join(lines[: max(sample_rows, 5)])
    dialect = _sniff_dialect(sample)
    reader = csv.reader(lines, dialect=dialect)
    parsed = [list(row) for row in reader]
    if not parsed:
        return {
            "parser": {"name": PARSER_NAME, "version": PARSER_VERSION},
            "text_segments": [],
            "tables": [],
            "warnings": warnings + [f"CSV is empty: {path}"],
        }

    headers = [cell.strip() or f"column_{i+1}" for i, cell in enumerate(parsed[0])]
    rows = _normalize_rows(parsed[1:])
    schema = infer_schema(headers, rows[:sample_rows])
    table = {
        "table_kind": "csv_table",
        "headers": headers,
        "rows": rows,
        "schema": schema.model_dump(),
        "metadata": {"delimiter": getattr(dialect, "delimiter", ",")},
        "locator": "csv:table#1",
    }
    return {
        "parser": {"name": PARSER_NAME, "version": PARSER_VERSION},
        "text_segments": [],
        "tables": [table],
        "warnings": warnings,
    }

