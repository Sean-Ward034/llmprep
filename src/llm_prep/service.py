"""Core ingest/diff/validate services shared by CLI, API, and MCP."""

from __future__ import annotations

import fnmatch
import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from llm_prep import SCHEMA_VERSION
from llm_prep.cache import CacheManager
from llm_prep.chunking import chunk_text, split_paragraphs
from llm_prep.extract.entities import extract_entities
from llm_prep.extract.task_spec import extract_tasks
from llm_prep.extract.tables import row_blocks, schema_signature
from llm_prep.ingest import detect_type, ingest_by_type
from llm_prep.manifest import build_manifest
from llm_prep.models import (
    ChunkMetadata,
    ChunkProvenance,
    ChunkRecord,
    DiffSummary,
    IngestResult,
    SourceInfo,
    TableBlockRecord,
    TableMetadata,
    TableProvenance,
    TableSchema,
    TaskSpecData,
    ValidateResult,
)
from llm_prep.normalize import (
    normalize_text,
    read_json,
    read_jsonl,
    sha256_file,
    sha256_text,
    stable_id,
    stable_json_dumps,
    write_json_atomic,
    write_jsonl_atomic,
)
from llm_prep.report import PipelineReport

logger = logging.getLogger("llm_prep")

SUPPORTED_FILES = {".csv", ".txt", ".md", ".html", ".htm", ".pdf", ".xlsx"}
REQUIRED_RAGPACK_FILES = {
    "manifest.json",
    "doc_chunks.jsonl",
    "tables.jsonl",
    "entities.json",
    "task_spec.json",
    "validation_report.json",
}


class LlmPrepError(RuntimeError):
    """Base error for LLM Prep operations."""


class InlinePayloadTooLarge(LlmPrepError):
    """Raised when inline output exceeds configured payload size cap."""


def _matches_globs(path: Path, globs: list[str]) -> bool:
    as_posix = path.as_posix()
    for pattern in globs:
        if pattern in {"*", "**", "**/*"}:
            return True
        if fnmatch.fnmatch(as_posix, pattern):
            return True
        if path.match(pattern):
            return True
        if fnmatch.fnmatch(path.name, pattern):
            return True
    return False


def resolve_sources(root: Path, include_globs: list[str], exclude_globs: list[str]) -> list[Path]:
    if root.is_file():
        return [root]
    files: list[Path] = []
    for file_path in root.rglob("*"):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in SUPPORTED_FILES:
            continue
        relative = file_path.relative_to(root)
        if include_globs and not _matches_globs(relative, include_globs):
            continue
        if exclude_globs and _matches_globs(relative, exclude_globs):
            continue
        files.append(file_path)
    files.sort(key=lambda p: p.as_posix().lower())
    return files


def _normalize_metadata(metadata: dict[str, Any]) -> ChunkMetadata:
    return ChunkMetadata(
        page=metadata.get("page"),
        section_heading=metadata.get("section_heading"),
        sheet=metadata.get("sheet"),
        row_start=metadata.get("row_start"),
        row_end=metadata.get("row_end"),
        email_subject=metadata.get("email_subject"),
        extra={
            key: value
            for key, value in metadata.items()
            if key not in {"page", "section_heading", "sheet", "row_start", "row_end", "email_subject"}
        },
    )


def _build_chunk_records(
    source_info: SourceInfo,
    segments: list[dict[str, Any]],
    chunk_target_chars: int,
) -> list[ChunkRecord]:
    records: list[ChunkRecord] = []
    for segment in segments:
        locator = segment.get("locator", "unknown")
        metadata = _normalize_metadata(segment.get("metadata") or {})
        paragraphs = split_paragraphs(segment.get("text", ""))
        if not paragraphs:
            paragraphs = [normalize_text(segment.get("text", ""))]
        chunks = chunk_text(paragraphs, target_chars=chunk_target_chars)
        for idx, text_chunk in enumerate(chunks, start=1):
            chunk_locator = f"{locator}#chunk={idx}"
            checksum = sha256_text(
                normalize_text(text_chunk)
                + "|"
                + stable_json_dumps(
                    {
                        "locator": chunk_locator,
                        "metadata": metadata.model_dump(),
                    }
                )
            )
            chunk_id = stable_id([source_info.source_id, chunk_locator, checksum])
            records.append(
                ChunkRecord(
                    chunk_id=chunk_id,
                    source_id=source_info.source_id,
                    source_path=source_info.path,
                    doc_type=source_info.type,
                    text=normalize_text(text_chunk),
                    metadata=metadata,
                    provenance=ChunkProvenance(locator=chunk_locator),
                    checksum=checksum,
                )
            )
    records.sort(key=lambda item: (item.chunk_id, item.provenance.locator))
    return records


def _build_table_records(
    source_info: SourceInfo,
    tables: list[dict[str, Any]],
    max_rows_per_block: int,
) -> list[TableBlockRecord]:
    records: list[TableBlockRecord] = []
    for table in tables:
        headers = table.get("headers", [])
        rows = table.get("rows", [])
        schema = TableSchema.model_validate(table.get("schema", {"columns": []}))
        metadata = table.get("metadata") or {}
        base_locator = table.get("locator", "table:unknown")
        kind = table.get("table_kind", "csv_table")
        for block_index, (row_start, row_end, block_data) in enumerate(
            row_blocks(rows, max_rows=max_rows_per_block),
            start=1,
        ):
            if not block_data:
                continue
            locator = f"{base_locator} row {row_start}-{row_end}"
            table_metadata = TableMetadata(
                sheet_name=metadata.get("sheet_name"),
                range=metadata.get("range"),
                html_table_index=metadata.get("html_table_index"),
                color_counts=metadata.get("color_counts", {}),
                row_block_index=block_index,
                extra={key: value for key, value in metadata.items() if key not in {"sheet_name", "range", "html_table_index", "color_counts"}},
            )
            checksum = sha256_text(
                stable_json_dumps(
                    {
                        "headers": headers,
                        "rows": block_data,
                        "row_start": row_start,
                        "row_end": row_end,
                    }
                )
            )
            table_id = stable_id([source_info.source_id, locator, schema_signature(schema)])
            records.append(
                TableBlockRecord(
                    table_id=table_id,
                    source_id=source_info.source_id,
                    source_path=source_info.path,
                    table_kind=kind,  # type: ignore[arg-type]
                    table_schema=schema,
                    row_start=row_start,
                    row_end=row_end,
                    data=block_data,
                    metadata=table_metadata,
                    provenance=TableProvenance(locator=locator),
                    checksum=checksum,
                )
            )
    records.sort(key=lambda item: (item.table_id, item.provenance.locator))
    return records


def _load_inline_artifacts(ragpack_dir: Path) -> dict[str, Any]:
    return {
        "manifest": read_json(ragpack_dir / "manifest.json"),
        "doc_chunks": read_jsonl(ragpack_dir / "doc_chunks.jsonl"),
        "tables": read_jsonl(ragpack_dir / "tables.jsonl"),
        "entities": read_json(ragpack_dir / "entities.json"),
        "task_spec": read_json(ragpack_dir / "task_spec.json"),
        "validation_report": read_json(ragpack_dir / "validation_report.json"),
    }


def _check_inline_size(payload: dict[str, Any], max_bytes: int) -> None:
    size = len(stable_json_dumps(payload).encode("utf-8"))
    if size > max_bytes:
        raise InlinePayloadTooLarge(
            f"Inline artifacts payload is {size} bytes, exceeds cap of {max_bytes}. Use output_mode=file."
        )


def ingest(
    *,
    source_path: Path,
    out_dir: Path,
    config: dict[str, Any],
    config_hash: str,
    force: bool = False,
    max_bytes: int | None = None,
    include_globs: list[str] | None = None,
    exclude_globs: list[str] | None = None,
    output_mode: str = "file",
    inline_max_bytes: int | None = None,
    deterministic_time: datetime | None = None,
) -> IngestResult:
    report = PipelineReport()
    log_events: list[dict[str, Any]] = []
    run_id = stable_id(
        [
            source_path.resolve().as_posix(),
            config_hash,
            deterministic_time.isoformat() if deterministic_time else datetime.now(timezone.utc).isoformat(),
        ]
    )
    ragpack_dir = out_dir / "ragpack"
    cache_dir = out_dir / ".llmprep_cache"
    log_events.append(
        {
            "event": "run_start",
            "run_id": run_id,
            "source_path": str(source_path.resolve()),
            "out_dir": str(out_dir.resolve()),
        }
    )

    if ragpack_dir.exists():
        if not force:
            raise LlmPrepError(f"Output directory already exists: {ragpack_dir}. Use --force to replace.")
        shutil.rmtree(ragpack_dir)
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
    ragpack_dir.mkdir(parents=True, exist_ok=True)
    cache = CacheManager(cache_dir)

    discovered_paths: list[Path] = []
    with report.timed("discover"):
        discovered_paths = resolve_sources(
            source_path,
            include_globs=include_globs or list(config.get("include_globs", ["**/*"])),
            exclude_globs=exclude_globs or list(config.get("exclude_globs", [])),
        )
    if not discovered_paths:
        raise LlmPrepError(f"No supported files found at: {source_path}")

    source_infos: list[SourceInfo] = []
    all_chunks: list[ChunkRecord] = []
    all_tables: list[TableBlockRecord] = []
    all_text_segments: list[dict[str, Any]] = []
    total_bytes = 0

    max_file_bytes = max_bytes or int(config.get("max_file_bytes", 10 * 1024 * 1024))

    with report.timed("ingest"):
        for path in discovered_paths:
            size = path.stat().st_size
            total_bytes += size
            log_events.append({"event": "source_discovered", "path": str(path.resolve()), "size_bytes": size})
            if size > max_file_bytes:
                report.warnings.append(f"Skipped {path} due to max_file_bytes={max_file_bytes}")
                log_events.append({"event": "source_skipped_max_bytes", "path": str(path.resolve())})
                continue
            source_type = detect_type(path)
            if not source_type:
                report.warnings.append(f"Unsupported file type: {path}")
                log_events.append({"event": "source_skipped_unsupported", "path": str(path.resolve())})
                continue

            file_sha = sha256_file(path)
            source_id = file_sha
            parse_key = CacheManager.compose_key(file_sha, "parse:v1", config_hash, "parse")
            cached = cache.get(parse_key)
            if cached:
                parsed = cached
                log_events.append({"event": "cache_hit", "key": parse_key, "path": str(path.resolve())})
            else:
                try:
                    parsed = ingest_by_type(path, source_type, config)
                except Exception as exc:  # noqa: BLE001
                    report.errors.append(f"Parse failed for {path}: {exc}")
                    log_events.append({"event": "parse_error", "path": str(path.resolve()), "error": str(exc)})
                    continue
                cache.put_stable(parse_key, parsed)
                log_events.append({"event": "cache_miss", "key": parse_key, "path": str(path.resolve())})

            parser = parsed.get("parser") or {"name": f"{source_type}_ingest", "version": "1.0.0"}
            source_info = SourceInfo(
                source_id=source_id,
                path=str(path.resolve()),
                type=source_type,  # type: ignore[arg-type]
                size_bytes=size,
                sha256=file_sha,
                mtime=path.stat().st_mtime,
                parser=parser,
            )
            source_infos.append(source_info)

            warnings = parsed.get("warnings", [])
            report.warnings.extend(warnings)

            text_segments = parsed.get("text_segments", [])
            for seg in text_segments:
                all_text_segments.append(
                    {
                        "source_id": source_id,
                        "source_path": str(path.resolve()),
                        "doc_type": source_type,
                        "text": seg.get("text", ""),
                        "metadata": seg.get("metadata", {}),
                        "locator": seg.get("locator", f"{source_type}:unknown"),
                    }
                )
            all_chunks.extend(
                _build_chunk_records(
                    source_info,
                    segments=text_segments,
                    chunk_target_chars=int(config.get("chunk_target_chars", 1000)),
                )
            )
            all_tables.extend(
                _build_table_records(
                    source_info,
                    tables=parsed.get("tables", []),
                    max_rows_per_block=int(config.get("xlsx_max_rows_per_block", 200)),
                )
            )

    with report.timed("extract"):
        entities = extract_entities(sources=source_infos, text_segments=all_text_segments, warnings=report.warnings)
        if config.get("enable_task_spec", True):
            task_spec = extract_tasks(all_text_segments)
        else:
            task_spec = TaskSpecData(schema_version=SCHEMA_VERSION, tasks=[])

    with report.timed("validate"):
        chunk_ids = [chunk.chunk_id for chunk in all_chunks]
        if len(chunk_ids) != len(set(chunk_ids)):
            report.errors.append("Duplicate chunk IDs detected")
        table_ids = [table.table_id for table in all_tables]
        if len(table_ids) != len(set(table_ids)):
            report.errors.append("Duplicate table IDs detected")

    report.metrics.update(
        {
            "sources": len(source_infos),
            "chunks": len(all_chunks),
            "tables": len(all_tables),
            "entities": len(entities.key_values),
            "tasks": len(getattr(task_spec, "tasks", [])),
            "total_bytes": total_bytes,
            "cache_hits": cache.hits,
            "cache_misses": cache.misses,
        }
    )

    with report.timed("write"):
        if deterministic_time is not None:
            report.timings = {stage: 0.0 for stage in report.timings}
        manifest = build_manifest(
            created_at=deterministic_time,
            config=config,
            sources=source_infos,
            chunk_count=len(all_chunks),
            table_count=len(all_tables),
            entity_count=len(entities.key_values),
            task_count=len(getattr(task_spec, "tasks", [])),
            cache_dir=str(cache_dir.resolve()),
            cache_hits=cache.hits,
            cache_misses=cache.misses,
        )
        report_model = report.to_model()

        write_json_atomic(ragpack_dir / "manifest.json", manifest.model_dump(mode="json"))
        write_jsonl_atomic(ragpack_dir / "doc_chunks.jsonl", [chunk.model_dump(mode="json") for chunk in all_chunks])
        write_jsonl_atomic(
            ragpack_dir / "tables.jsonl",
            [table.model_dump(mode="json", by_alias=True) for table in all_tables],
        )
        write_json_atomic(ragpack_dir / "entities.json", entities.model_dump(mode="json"))
        write_json_atomic(ragpack_dir / "task_spec.json", task_spec.model_dump(mode="json"))
        write_json_atomic(ragpack_dir / "validation_report.json", report_model.model_dump(mode="json"))
        log_events.append(
            {
                "event": "artifacts_written",
                "chunks": len(all_chunks),
                "tables": len(all_tables),
                "warnings": len(report.warnings),
                "errors": len(report.errors),
            }
        )
        write_jsonl_atomic(ragpack_dir / "run_log.jsonl", log_events)

    inline_artifacts: dict[str, Any] | None = None
    if output_mode == "inline":
        inline_payload = _load_inline_artifacts(ragpack_dir)
        max_inline = inline_max_bytes or int(config.get("api", {}).get("inline_max_bytes", 10_485_760))
        _check_inline_size(inline_payload, max_inline)
        inline_artifacts = inline_payload

    return IngestResult(
        run_id=run_id,
        ragpack_dir=str(ragpack_dir.resolve()),
        manifest_path=str((ragpack_dir / "manifest.json").resolve()),
        stats={
            "sources": len(source_infos),
            "chunks": len(all_chunks),
            "tables": len(all_tables),
            "entities": len(entities.key_values),
            "tasks": len(getattr(task_spec, "tasks", [])),
        },
        warnings=report.warnings,
        cache=manifest.cache,
        inline_artifacts=inline_artifacts,
    )


def diff(*, old_ragpack: Path, new_ragpack: Path, out_dir: Path) -> DiffSummary:
    old_chunks = {row["chunk_id"]: row for row in read_jsonl(old_ragpack / "doc_chunks.jsonl")}
    new_chunks = {row["chunk_id"]: row for row in read_jsonl(new_ragpack / "doc_chunks.jsonl")}
    old_tables = {row["table_id"]: row for row in read_jsonl(old_ragpack / "tables.jsonl")}
    new_tables = {row["table_id"]: row for row in read_jsonl(new_ragpack / "tables.jsonl")}

    def _delta(old_map: dict[str, Any], new_map: dict[str, Any], checksum_key: str) -> tuple[list[Any], dict[str, int]]:
        added = [new_map[key] for key in sorted(new_map.keys() - old_map.keys())]
        removed = [old_map[key] for key in sorted(old_map.keys() - new_map.keys())]
        changed = [
            new_map[key]
            for key in sorted(new_map.keys() & old_map.keys())
            if new_map[key].get(checksum_key) != old_map[key].get(checksum_key)
        ]
        counts = {"added": len(added), "removed": len(removed), "changed": len(changed)}
        return added + changed, counts

    changed_chunks, chunk_counts = _delta(old_chunks, new_chunks, "checksum")
    changed_tables, table_counts = _delta(old_tables, new_tables, "checksum")

    out_dir.mkdir(parents=True, exist_ok=True)
    summary = DiffSummary(schema_version=SCHEMA_VERSION, chunks=chunk_counts, tables=table_counts)
    write_json_atomic(out_dir / "diff_summary.json", summary.model_dump(mode="json"))
    write_jsonl_atomic(out_dir / "changed_chunks.jsonl", changed_chunks)
    write_jsonl_atomic(out_dir / "changed_tables.jsonl", changed_tables)
    return summary


def validate(*, ragpack_dir: Path) -> ValidateResult:
    errors: list[str] = []
    warnings: list[str] = []

    if not ragpack_dir.exists():
        raise LlmPrepError(f"Ragpack directory not found: {ragpack_dir}")

    missing = sorted(name for name in REQUIRED_RAGPACK_FILES if not (ragpack_dir / name).exists())
    if missing:
        errors.append(f"Missing required files: {', '.join(missing)}")

    chunks: list[dict[str, Any]] = []
    tables: list[dict[str, Any]] = []
    report_data: dict[str, Any] = {}
    if not missing:
        try:
            chunks = read_jsonl(ragpack_dir / "doc_chunks.jsonl")
            tables = read_jsonl(ragpack_dir / "tables.jsonl")
            report_data = read_json(ragpack_dir / "validation_report.json")
        except (json.JSONDecodeError, OSError) as exc:
            errors.append(f"Invalid artifact JSON/JSONL: {exc}")

    chunk_ids = [row.get("chunk_id") for row in chunks]
    if len(chunk_ids) != len(set(chunk_ids)):
        errors.append("Duplicate chunk IDs detected")
    table_ids = [row.get("table_id") for row in tables]
    if len(table_ids) != len(set(table_ids)):
        errors.append("Duplicate table IDs detected")

    parse_errors = report_data.get("errors", []) if report_data else []
    if parse_errors:
        errors.append(f"Parse errors present: {len(parse_errors)}")

    unknown_colors = []
    for table in tables:
        metadata = table.get("metadata", {})
        color_counts = metadata.get("color_counts", {}) or {}
        unknown = [key for key in color_counts.keys() if str(key).startswith("UNKNOWN:")]
        unknown_colors.extend(unknown)
    if unknown_colors:
        errors.append("Unknown tiers/colors exist in XLSX metadata")

    for row in chunks:
        if not row.get("text"):
            warnings.append(f"Chunk with empty text: {row.get('chunk_id', 'unknown')}")

    report_path = ragpack_dir / "validation_report.json"
    return ValidateResult(ok=not errors, report_path=str(report_path.resolve()), errors=errors, warnings=warnings)


def schema_snapshot() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "required_files": sorted(REQUIRED_RAGPACK_FILES),
        "commands": ["ingest", "diff", "validate", "serve", "mcp"],
        "api": {
            "routes": ["POST /v1/ingest", "POST /v1/diff", "POST /v1/validate", "GET /v1/health", "GET /v1/schema"],
            "default_output_mode": "file",
            "inline_cap_default": 10_485_760,
        },
        "mcp_tools": ["llmprep_ingest", "llmprep_diff", "llmprep_validate"],
    }


def ensure_valid_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise LlmPrepError(f"Invalid deterministic-time value: {value}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def validate_config_shape(config: dict[str, Any]) -> None:
    required = [
        "chunk_target_chars",
        "max_file_bytes",
        "csv_sample_rows",
        "xlsx_max_rows_per_block",
        "include_globs",
        "exclude_globs",
        "enable_task_spec",
    ]
    for key in required:
        if key not in config:
            raise LlmPrepError(f"Missing config key: {key}")
    try:
        json.dumps(config)
    except TypeError as exc:
        raise LlmPrepError("Config contains non-serializable values") from exc
