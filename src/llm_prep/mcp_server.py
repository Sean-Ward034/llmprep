"""MCP stdio server exposing llmprep operations as tools."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from llm_prep.config import build_config
from llm_prep.service import (
    InlinePayloadTooLarge,
    LlmPrepError,
    diff,
    ingest,
    validate,
    validate_config_shape,
)

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:  # pragma: no cover
    FastMCP = None  # type: ignore[assignment]


if FastMCP is None:  # pragma: no cover
    mcp = None
else:
    mcp = FastMCP("llmprep")


def llmprep_ingest(
    path: str,
    out_dir: str,
    force: bool = False,
    max_bytes: int | None = None,
    include_globs: list[str] | None = None,
    exclude_globs: list[str] | None = None,
    config_overrides: dict[str, Any] | None = None,
    output_mode: str = "file",
    inline_max_bytes: int | None = None,
    deterministic_time: str | None = None,
) -> dict[str, Any]:
    try:
        config, cfg_hash, _ = build_config(runtime_overrides=config_overrides or {})
        validate_config_shape(config)
        from llm_prep.service import ensure_valid_datetime

        result = ingest(
            source_path=Path(path),
            out_dir=Path(out_dir),
            config=config,
            config_hash=cfg_hash,
            force=force,
            max_bytes=max_bytes,
            include_globs=include_globs,
            exclude_globs=exclude_globs,
            output_mode=output_mode,
            inline_max_bytes=inline_max_bytes,
            deterministic_time=ensure_valid_datetime(deterministic_time),
        )
        return result.model_dump(mode="json")
    except (LlmPrepError, InlinePayloadTooLarge) as exc:
        return {"error": str(exc), "ok": False}


def llmprep_diff(old: str, new: str, out_dir: str) -> dict[str, Any]:
    try:
        summary = diff(old_ragpack=Path(old), new_ragpack=Path(new), out_dir=Path(out_dir))
        return summary.model_dump(mode="json")
    except LlmPrepError as exc:
        return {"error": str(exc), "ok": False}


def llmprep_validate(ragpack_dir: str) -> dict[str, Any]:
    try:
        result = validate(ragpack_dir=Path(ragpack_dir))
        return result.model_dump(mode="json")
    except LlmPrepError as exc:
        return {"error": str(exc), "ok": False}


def run_mcp_server() -> None:
    if mcp is None:  # pragma: no cover
        raise RuntimeError("The 'mcp' package is required for `llmprep mcp`.")
    mcp.run()


if mcp is not None:  # pragma: no cover
    mcp.tool()(llmprep_ingest)
    mcp.tool()(llmprep_diff)
    mcp.tool()(llmprep_validate)
