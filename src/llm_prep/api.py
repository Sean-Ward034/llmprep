"""Local HTTP API server."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException

from llm_prep import __version__
from llm_prep.config import build_config
from llm_prep.models import DiffRequest, HealthResponse, IngestRequest, ValidateRequest
from llm_prep.service import (
    InlinePayloadTooLarge,
    LlmPrepError,
    diff,
    ingest,
    schema_snapshot,
    validate,
    validate_config_shape,
)


def create_app() -> FastAPI:
    app = FastAPI(title="LLM Prep API", version=__version__)

    @app.get("/v1/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(version=__version__)

    @app.get("/v1/schema")
    def schema() -> dict:
        return schema_snapshot()

    @app.post("/v1/ingest")
    def ingest_endpoint(payload: IngestRequest) -> dict:
        try:
            runtime_overrides = payload.config_overrides or {}
            config, cfg_hash, _ = build_config(runtime_overrides=runtime_overrides)
            validate_config_shape(config)
            result = ingest(
                source_path=Path(payload.path),
                out_dir=Path(payload.out_dir),
                config=config,
                config_hash=cfg_hash,
                force=payload.force,
                max_bytes=payload.max_bytes,
                include_globs=payload.include_globs,
                exclude_globs=payload.exclude_globs,
                output_mode=payload.output_mode,
                inline_max_bytes=payload.inline_max_bytes,
                deterministic_time=payload.deterministic_time,
            )
            return result.model_dump(mode="json")
        except InlinePayloadTooLarge as exc:
            raise HTTPException(status_code=413, detail=str(exc)) from exc
        except LlmPrepError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/v1/diff")
    def diff_endpoint(payload: DiffRequest) -> dict:
        try:
            summary = diff(old_ragpack=Path(payload.old), new_ragpack=Path(payload.new), out_dir=Path(payload.out_dir))
            return summary.model_dump(mode="json")
        except LlmPrepError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/v1/validate")
    def validate_endpoint(payload: ValidateRequest) -> dict:
        try:
            result = validate(ragpack_dir=Path(payload.ragpack_dir))
            return result.model_dump(mode="json")
        except LlmPrepError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    return app

