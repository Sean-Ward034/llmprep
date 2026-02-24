"""Manifest construction helpers."""

from __future__ import annotations

from datetime import datetime, timezone

from llm_prep import SCHEMA_VERSION, __version__
from llm_prep.models import Manifest, ManifestCache, ManifestStats, SourceInfo


def build_manifest(
    *,
    created_at: datetime | None,
    config: dict,
    sources: list[SourceInfo],
    chunk_count: int,
    table_count: int,
    entity_count: int,
    task_count: int,
    cache_dir: str,
    cache_hits: int,
    cache_misses: int,
) -> Manifest:
    timestamp = created_at or datetime.now(timezone.utc)
    return Manifest(
        schema_version=SCHEMA_VERSION,
        tool_version=__version__,
        created_at=timestamp,
        config=config,
        sources=sources,
        stats=ManifestStats(
            chunks=chunk_count,
            tables=table_count,
            entities=entity_count,
            tasks=task_count,
        ),
        cache=ManifestCache(
            enabled=True,
            cache_dir=cache_dir,
            hits=cache_hits,
            misses=cache_misses,
        ),
    )

