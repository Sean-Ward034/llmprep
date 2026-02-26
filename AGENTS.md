# AGENTS.md

## Cursor Cloud specific instructions

### Overview

`llmprep` is a local-first Python CLI/API/MCP tool that ingests documents (PDF, XLSX, CSV, HTML, text) into deterministic LLM-ready artifact packs ("ragpacks"). No database, Docker, or external services required.

### Development commands

- **Install**: `pip install ".[dev]"` (see `pyproject.toml` for deps; uses hatchling build backend)
- **Tests**: `python3 -m pytest` (16 tests covering all subsystems)
- **Smoke test**: `python3 scripts/smoke_integrations.py`
- **CLI**: `llmprep ingest <dir> --out <dir> --force`
- **HTTP API**: `llmprep serve --host 127.0.0.1 --port 8741`
- **MCP server**: `llmprep mcp`

### Caveats

- The `llmprep` script installs to `~/.local/bin`. This directory is added to `PATH` in `~/.bashrc`; if a new shell doesn't pick it up, run `export PATH="$HOME/.local/bin:$PATH"`.
- Use `python3` not `python` — this environment does not alias `python` to `python3`.
- No linting tools (ruff, flake8, mypy, etc.) are configured in this project. CI only runs `pytest` and the smoke script.
- The project is pure Python with no external service dependencies. All I/O is filesystem-based.
