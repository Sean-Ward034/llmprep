"""Smoke checks for integration templates and MCP startup."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REQUIRED_TEMPLATES = [
    Path("templates/integrations/codex/config.toml"),
    Path("templates/integrations/claude/.mcp.json"),
    Path("templates/integrations/cursor/mcp.json"),
    Path("templates/integrations/codebuff/mcp.json"),
]


def check_templates() -> None:
    missing = [str(path) for path in REQUIRED_TEMPLATES if not path.exists()]
    if missing:
        raise RuntimeError(f"Missing integration templates: {', '.join(missing)}")


def check_mcp_boot() -> None:
    cmd = [sys.executable, "-m", "llm_prep.cli", "mcp"]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        proc.wait(timeout=1.5)
    except subprocess.TimeoutExpired:
        proc.terminate()
        proc.wait(timeout=5)
        return
    stderr = proc.stderr.read() if proc.stderr else ""
    raise RuntimeError(f"MCP server exited early with code {proc.returncode}: {stderr}")


def main() -> int:
    check_templates()
    check_mcp_boot()
    print("Integration smoke checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

