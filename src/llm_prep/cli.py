"""Typer CLI for LLM Prep."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
import uvicorn
from rich.console import Console
from rich.table import Table

from llm_prep.api import create_app
from llm_prep.config import ConfigError, build_config
from llm_prep.mcp_server import run_mcp_server
from llm_prep.normalize import stable_json_dumps
from llm_prep.service import (
    InlinePayloadTooLarge,
    LlmPrepError,
    diff,
    ensure_valid_datetime,
    ingest,
    validate,
    validate_config_shape,
)

app = typer.Typer(help="Deterministic ingestion + cache for LLM-ready artifacts.")
console = Console()

EXIT_OK = 0
EXIT_VALIDATION_ERROR = 2
EXIT_RUNTIME_ERROR = 3
EXIT_CONFIG_ERROR = 4


def _print_payload(payload: dict, as_json: bool) -> None:
    if as_json:
        console.print(stable_json_dumps(payload))
        return
    table = Table(show_header=False, box=None)
    for key, value in payload.items():
        table.add_row(str(key), str(value))
    console.print(table)


@app.command("ingest")
def ingest_command(
    path: Path = typer.Argument(..., help="Input file or directory."),
    out: Path = typer.Option(..., "--out", help="Output directory for ragpack."),
    force: bool = typer.Option(False, "--force", help="Replace existing ragpack output."),
    max_bytes: Optional[int] = typer.Option(None, "--max-bytes", help="Max source file size in bytes."),
    include_globs: list[str] = typer.Option([], "--include-globs", help="Include glob(s). Repeat flag to add more."),
    exclude_globs: list[str] = typer.Option([], "--exclude-globs", help="Exclude glob(s). Repeat flag to add more."),
    config: Optional[Path] = typer.Option(None, "--config", help="Path to llmprep.toml/yaml."),
    output_mode: str = typer.Option("file", "--output-mode", help="file or inline."),
    inline_max_bytes: Optional[int] = typer.Option(None, "--inline-max-bytes", help="Inline response max bytes."),
    deterministic_time: Optional[str] = typer.Option(None, "--deterministic-time", help="Fixed timestamp (ISO8601)."),
    json_output: bool = typer.Option(False, "--json", help="Print machine-readable JSON."),
) -> None:
    try:
        cli_overrides = {
            "max_file_bytes": max_bytes,
            "include_globs": include_globs or None,
            "exclude_globs": exclude_globs or None,
            "api.inline_max_bytes": inline_max_bytes,
            "api.default_output_mode": output_mode,
        }
        cfg, cfg_hash, _ = build_config(config_path=config, cli_overrides=cli_overrides)
        validate_config_shape(cfg)
        result = ingest(
            source_path=path,
            out_dir=out,
            config=cfg,
            config_hash=cfg_hash,
            force=force,
            max_bytes=max_bytes,
            include_globs=include_globs or None,
            exclude_globs=exclude_globs or None,
            output_mode=output_mode,
            inline_max_bytes=inline_max_bytes,
            deterministic_time=ensure_valid_datetime(deterministic_time),
        )
        _print_payload(result.model_dump(mode="json"), as_json=json_output)
        raise typer.Exit(code=EXIT_OK)
    except ConfigError as exc:
        _print_payload({"error": str(exc), "code": EXIT_CONFIG_ERROR}, as_json=json_output)
        raise typer.Exit(code=EXIT_CONFIG_ERROR) from exc
    except InlinePayloadTooLarge as exc:
        _print_payload({"error": str(exc), "code": EXIT_VALIDATION_ERROR}, as_json=json_output)
        raise typer.Exit(code=EXIT_VALIDATION_ERROR) from exc
    except LlmPrepError as exc:
        _print_payload({"error": str(exc), "code": EXIT_RUNTIME_ERROR}, as_json=json_output)
        raise typer.Exit(code=EXIT_RUNTIME_ERROR) from exc


@app.command("diff")
def diff_command(
    old: Path = typer.Option(..., "--old", help="Previous ragpack directory."),
    new: Path = typer.Option(..., "--new", help="Current ragpack directory."),
    out: Path = typer.Option(..., "--out", help="Output directory for diff artifacts."),
    json_output: bool = typer.Option(False, "--json", help="Print machine-readable JSON."),
) -> None:
    try:
        summary = diff(old_ragpack=old, new_ragpack=new, out_dir=out)
        _print_payload(summary.model_dump(mode="json"), as_json=json_output)
        raise typer.Exit(code=EXIT_OK)
    except LlmPrepError as exc:
        _print_payload({"error": str(exc), "code": EXIT_RUNTIME_ERROR}, as_json=json_output)
        raise typer.Exit(code=EXIT_RUNTIME_ERROR) from exc


@app.command("validate")
def validate_command(
    ragpack_dir: Path = typer.Argument(..., help="Ragpack directory."),
    json_output: bool = typer.Option(False, "--json", help="Print machine-readable JSON."),
) -> None:
    try:
        result = validate(ragpack_dir=ragpack_dir)
        code = EXIT_OK if result.ok else EXIT_VALIDATION_ERROR
        _print_payload(result.model_dump(mode="json"), as_json=json_output)
        raise typer.Exit(code=code)
    except LlmPrepError as exc:
        _print_payload({"error": str(exc), "code": EXIT_RUNTIME_ERROR}, as_json=json_output)
        raise typer.Exit(code=EXIT_RUNTIME_ERROR) from exc


@app.command("serve")
def serve_command(
    host: str = typer.Option("127.0.0.1", "--host", help="HTTP bind host."),
    port: int = typer.Option(8741, "--port", help="HTTP bind port."),
    timeout_seconds: int = typer.Option(600, "--timeout-seconds", help="Synchronous request timeout."),
) -> None:
    app_instance = create_app()
    uvicorn.run(app_instance, host=host, port=port, timeout_keep_alive=timeout_seconds)


@app.command("mcp")
def mcp_command() -> None:
    run_mcp_server()


if __name__ == "__main__":
    app()

