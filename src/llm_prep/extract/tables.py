"""Table schema/type inference helpers."""

from __future__ import annotations

import datetime as dt
from typing import Any

from llm_prep.models import TableColumn, TableSchema
from llm_prep.normalize import stable_json_dumps


def infer_scalar_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int) and not isinstance(value, bool):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, (dt.date, dt.datetime)):
        return "date"
    if isinstance(value, str):
        if value.lower() in {"true", "false"}:
            return "bool"
        try:
            int(value)
            return "int"
        except ValueError:
            pass
        try:
            float(value)
            return "float"
        except ValueError:
            pass
        return "string"
    return "string"


def infer_schema(headers: list[str], rows: list[list[Any]]) -> TableSchema:
    cols: list[TableColumn] = []
    for idx, header in enumerate(headers):
        inferred = "string"
        for row in rows:
            if idx >= len(row):
                continue
            t = infer_scalar_type(row[idx])
            if t != "null":
                inferred = t
                break
        cols.append(TableColumn(name=header or f"column_{idx+1}", index=idx, inferred_type=inferred))
    return TableSchema(columns=cols)


def schema_signature(schema: TableSchema) -> str:
    return stable_json_dumps(schema.model_dump())


def row_blocks(rows: list[list[Any]], max_rows: int) -> list[tuple[int, int, list[list[Any]]]]:
    blocks: list[tuple[int, int, list[list[Any]]]] = []
    start = 1
    for i in range(0, len(rows), max_rows):
        subset = rows[i : i + max_rows]
        end = start + len(subset) - 1
        blocks.append((start, end, subset))
        start = end + 1
    return blocks

