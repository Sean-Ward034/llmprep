# llmprep

`llmprep` is a local-first, deterministic ingestion engine for turning mixed client artifacts into inspectable LLM-ready outputs.

## What it does

- Ingests `pdf`, `xlsx`, `csv`, `html`, and `text` files.
- Produces deterministic artifact packs (`ragpack`) with chunks, table blocks, entities, task heuristics, and validation report.
- Caches parse/chunk stages by file hash + parser version + config hash.
- Exposes three integration surfaces:
  - CLI (`llmprep ...`)
  - Local HTTP API (`llmprep serve`)
  - MCP stdio server (`llmprep mcp`)

## Install

### With uvx (recommended)

```bash
uvx llmprep --help
```

### With pip

```bash
pip install llmprep
llmprep --help
```

### Development

```bash
pip install ".[dev]"
pytest
```

## CLI examples

### Ingest

```bash
llmprep ingest ./inputs --out ./out --force
```

```bash
llmprep ingest ./inputs --out ./out --output-mode inline --inline-max-bytes 10485760 --json
```

### Diff

```bash
llmprep diff --old ./out_old/ragpack --new ./out_new/ragpack --out ./diff
```

### Validate

```bash
llmprep validate ./out/ragpack
```

### Serve API

```bash
llmprep serve --host 127.0.0.1 --port 8741
```

### Run MCP server

```bash
llmprep mcp
```

## Output files

`<out>/ragpack/`:

- `manifest.json`
- `doc_chunks.jsonl`
- `tables.jsonl`
- `entities.json`
- `task_spec.json`
- `validation_report.json`
- `run_log.jsonl` (structured local events)

All top-level artifacts include `schema_version = "1.0.0"`.

## Caching

Default cache directory:

- `<out>/.llmprep_cache/`

Cache key:

- `sha256(file bytes) + parser_version + config_hash + stage`

Cache tracks hits/misses and is recorded in `manifest.json`.

## Configuration

Supported config files:

- `llmprep.toml`
- `llmprep.yaml` / `llmprep.yml`
- `llmprep.example.toml` is provided as a template

Precedence:

- CLI flags > config file > defaults

Important keys:

- `chunk_target_chars`
- `max_file_bytes`
- `csv_sample_rows`
- `xlsx_max_rows_per_block`
- `include_globs`
- `exclude_globs`
- `enable_task_spec`
- `api.default_output_mode`
- `api.inline_max_bytes`
- `api.timeout_seconds`
- `api.host`
- `api.port`
- `features.pro_enabled`
- `licensing.provider`

## HTTP API

Routes:

- `POST /v1/ingest`
- `POST /v1/diff`
- `POST /v1/validate`
- `GET /v1/health`
- `GET /v1/schema`

`/v1/ingest` supports `file` and `inline` output modes.
Default mode is `file`.
Inline mode enforces a hard payload cap (default `10_485_760` bytes).

## Privacy

`llmprep` is local-first and does not upload files or send telemetry by default.

## Known limitations

- No OCR in MVP (scanned PDFs produce warning).
- No `.eml` parsing in MVP.
- No hosted service/auth/tenancy in MVP.
- No vector database integrations in MVP.

## Integrations

Templates and setup guides for OpenAI Codex, Claude Code, Cursor, and Codebuff are in:

- `templates/integrations/`
- `docs/integrations.md`

## License

Apache-2.0
