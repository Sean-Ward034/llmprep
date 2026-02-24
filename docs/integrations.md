# Integrations: Codex, Claude Code, Cursor, Codebuff

This project exposes `llmprep` via CLI, local HTTP API, and MCP (`llmprep mcp`).

## Common requirement

- Install package: `uvx llmprep --help` or `pip install llmprep`
- Ensure `llmprep` is available on PATH for your tool runtime.

## OpenAI Codex

Use the template at `templates/integrations/codex/config.toml`.

Expected shape:

```toml
[mcp_servers.llmprep]
command = "llmprep"
args = ["mcp"]
```

## Claude Code

Use the template at `templates/integrations/claude/.mcp.json`.

Expected shape:

```json
{
  "mcpServers": {
    "llmprep": {
      "command": "llmprep",
      "args": ["mcp"]
    }
  }
}
```

## Cursor

Use the template at `templates/integrations/cursor/mcp.json`.

Expected shape:

```json
{
  "mcpServers": {
    "llmprep": {
      "command": "llmprep",
      "args": ["mcp"]
    }
  }
}
```

If using `cursor-agent`, load the same MCP config and verify tool discovery.

## Codebuff

Use the template at `templates/integrations/codebuff/mcp.json`.

For environments where MCP wiring is not available yet, use the CLI fallback wrapper:

```bash
python scripts/codebuff_cli_fallback.py --path ./inputs --out ./out --print --json
```

## API integration option

Run local API:

```bash
llmprep serve --host 127.0.0.1 --port 8741
```

Then call:

- `POST /v1/ingest`
- `POST /v1/diff`
- `POST /v1/validate`

## Smoke tests

Run integration smoke checks:

```bash
python scripts/smoke_integrations.py
```

What this verifies:

- required template files exist
- MCP entrypoint imports
- MCP server process starts without immediate crash

## Troubleshooting

- `command not found: llmprep`
  - install with `uvx` or add Python scripts directory to PATH.
- MCP server exits immediately
  - run `llmprep mcp` directly to inspect errors.
- API call returns `413`
  - inline payload exceeded cap; use `output_mode=file` or raise `inline_max_bytes`.
