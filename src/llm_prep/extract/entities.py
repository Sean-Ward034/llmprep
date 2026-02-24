"""Heuristic entity extraction for headings and key-value pairs."""

from __future__ import annotations

import re
from typing import Iterable

from llm_prep import SCHEMA_VERSION
from llm_prep.chunking import is_heading
from llm_prep.models import EntitiesData, SourceInfo


def extract_entities(
    *,
    sources: list[SourceInfo],
    text_segments: Iterable[dict],
    warnings: list[str] | None = None,
) -> EntitiesData:
    headings: list[str] = []
    key_values: list[dict[str, str]] = []
    seen_headings: set[str] = set()

    for seg in text_segments:
        text = seg.get("text", "")
        for line in text.splitlines():
            candidate = line.strip()
            if not candidate:
                continue
            if is_heading(candidate) and candidate not in seen_headings:
                seen_headings.add(candidate)
                headings.append(candidate)
            match = re.match(r"^([A-Za-z0-9 _/()-]{1,80}):\s+(.+)$", candidate)
            if match:
                key_values.append(
                    {
                        "label": match.group(1).strip(),
                        "value": match.group(2).strip(),
                    }
                )

    files = [
        {
            "source_id": source.source_id,
            "path": source.path,
            "type": source.type,
            "size_bytes": source.size_bytes,
            "sha256": source.sha256,
        }
        for source in sources
    ]

    return EntitiesData(
        schema_version=SCHEMA_VERSION,
        files=files,
        headings=headings,
        key_values=key_values,
        warnings=warnings or [],
    )

