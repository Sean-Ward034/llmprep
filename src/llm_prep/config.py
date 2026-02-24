"""Configuration loading and precedence handling."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

from llm_prep import __version__, SCHEMA_VERSION
from llm_prep.normalize import sha256_text, stable_json_dumps

DEFAULT_CONFIG: dict[str, Any] = {
    "schema_version": SCHEMA_VERSION,
    "tool_version": __version__,
    "chunk_target_chars": 1000,
    "max_file_bytes": 10 * 1024 * 1024,
    "csv_sample_rows": 50,
    "xlsx_max_rows_per_block": 200,
    "include_globs": ["**/*"],
    "exclude_globs": [],
    "enable_task_spec": True,
    "api": {
        "default_output_mode": "file",
        "inline_max_bytes": 10_485_760,
        "timeout_seconds": 600,
        "host": "127.0.0.1",
        "port": 8741,
    },
    "features": {
        "pro_enabled": False,
    },
    "licensing": {
        "provider": "noop",
    },
}


class ConfigError(ValueError):
    """Raised for invalid config files."""


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(base)
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _load_toml(path: Path) -> dict[str, Any]:
    import tomllib

    with path.open("rb") as handle:
        return tomllib.load(handle)


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle)
    return loaded or {}


def load_config_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ConfigError(f"Config path does not exist: {path}")
    suffix = path.suffix.lower()
    if suffix == ".toml":
        return _load_toml(path)
    if suffix in {".yaml", ".yml"}:
        return _load_yaml(path)
    raise ConfigError(f"Unsupported config format: {path.suffix}")


def discover_config_path(explicit: Path | None = None, cwd: Path | None = None) -> Path | None:
    if explicit:
        return explicit
    root = cwd or Path.cwd()
    for candidate in ("llmprep.toml", "llmprep.yaml", "llmprep.yml"):
        path = root / candidate
        if path.exists():
            return path
    return None


def apply_cli_overrides(config: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(config)
    for key, value in overrides.items():
        if value is None:
            continue
        if "." in key:
            cursor = merged
            parts = key.split(".")
            for part in parts[:-1]:
                if part not in cursor or not isinstance(cursor[part], dict):
                    cursor[part] = {}
                cursor = cursor[part]
            cursor[parts[-1]] = value
        else:
            merged[key] = value
    return merged


def build_config(
    config_path: Path | None = None,
    cli_overrides: dict[str, Any] | None = None,
    runtime_overrides: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], str, Path | None]:
    resolved = deepcopy(DEFAULT_CONFIG)
    discovered_path = discover_config_path(config_path)
    if discovered_path:
        file_cfg = load_config_file(discovered_path)
        resolved = _deep_merge(resolved, file_cfg)
    if runtime_overrides:
        resolved = _deep_merge(resolved, runtime_overrides)
    if cli_overrides:
        resolved = apply_cli_overrides(resolved, cli_overrides)
    cfg_hash = sha256_text(stable_json_dumps(resolved))
    return resolved, cfg_hash, discovered_path

