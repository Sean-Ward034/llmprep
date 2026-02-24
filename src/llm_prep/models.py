"""Pydantic models for LLM Prep artifacts and API contracts."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


SourceType = Literal["pdf", "xlsx", "csv", "html", "text"]
OutputMode = Literal["file", "inline"]
TableKind = Literal["xlsx_sheet_table", "html_table", "csv_table"]


class ParserInfo(BaseModel):
    name: str
    version: str


class SourceInfo(BaseModel):
    source_id: str
    path: str
    type: SourceType
    size_bytes: int
    sha256: str
    mtime: float
    parser: ParserInfo


class ChunkMetadata(BaseModel):
    page: int | None = None
    section_heading: str | None = None
    sheet: str | None = None
    row_start: int | None = None
    row_end: int | None = None
    email_subject: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class ChunkProvenance(BaseModel):
    locator: str


class ChunkRecord(BaseModel):
    chunk_id: str
    source_id: str
    source_path: str
    doc_type: SourceType
    text: str
    metadata: ChunkMetadata
    provenance: ChunkProvenance
    checksum: str


class TableColumn(BaseModel):
    name: str
    index: int
    inferred_type: str


class TableSchema(BaseModel):
    columns: list[TableColumn]


class TableMetadata(BaseModel):
    sheet_name: str | None = None
    range: str | None = None
    html_table_index: int | None = None
    color_counts: dict[str, int] = Field(default_factory=dict)
    row_block_index: int = 0
    extra: dict[str, Any] = Field(default_factory=dict)


class TableProvenance(BaseModel):
    locator: str


class TableBlockRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    table_id: str
    source_id: str
    source_path: str
    table_kind: TableKind
    table_schema: TableSchema = Field(alias="schema")
    row_start: int
    row_end: int
    data: list[list[Any]]
    metadata: TableMetadata
    provenance: TableProvenance
    checksum: str


class EntitiesData(BaseModel):
    schema_version: str
    files: list[dict[str, Any]]
    headings: list[str]
    key_values: list[dict[str, str]]
    warnings: list[str]


class TaskItem(BaseModel):
    id: str
    title: str
    description: str
    priority_hint: str | None = None
    source_locator: str
    confidence: float


class TaskSpecData(BaseModel):
    schema_version: str
    tasks: list[TaskItem]


class ValidationReport(BaseModel):
    schema_version: str
    errors: list[str]
    warnings: list[str]
    metrics: dict[str, Any]
    timing_breakdown: dict[str, float]


class ManifestCache(BaseModel):
    enabled: bool
    cache_dir: str
    hits: int
    misses: int


class ManifestStats(BaseModel):
    chunks: int
    tables: int
    entities: int
    tasks: int


class Manifest(BaseModel):
    schema_version: str
    tool_version: str
    created_at: datetime
    config: dict[str, Any]
    sources: list[SourceInfo]
    stats: ManifestStats
    cache: ManifestCache


class IngestResult(BaseModel):
    run_id: str
    ragpack_dir: str
    manifest_path: str
    stats: dict[str, int]
    warnings: list[str]
    cache: ManifestCache
    inline_artifacts: dict[str, Any] | None = None


class DiffSummary(BaseModel):
    schema_version: str
    chunks: dict[str, int]
    tables: dict[str, int]


class ValidateResult(BaseModel):
    ok: bool
    report_path: str
    errors: list[str]
    warnings: list[str]


class IngestRequest(BaseModel):
    path: str
    out_dir: str
    force: bool = False
    max_bytes: int | None = None
    include_globs: list[str] | None = None
    exclude_globs: list[str] | None = None
    config_overrides: dict[str, Any] | None = None
    output_mode: OutputMode = "file"
    inline_max_bytes: int | None = None
    deterministic_time: datetime | None = None


class DiffRequest(BaseModel):
    old: str
    new: str
    out_dir: str


class ValidateRequest(BaseModel):
    ragpack_dir: str


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    version: str
