"""Filesystem cache for deterministic pipeline stages."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from llm_prep.normalize import read_json, sha256_text, stable_json_dumps, write_json_atomic


class CacheManager:
    def __init__(self, cache_dir: Path, enabled: bool = True) -> None:
        self.cache_dir = cache_dir
        self.enabled = enabled
        self.hits = 0
        self.misses = 0
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def compose_key(file_sha256: str, parser_version: str, config_hash: str, stage: str) -> str:
        return sha256_text(f"{file_sha256}:{parser_version}:{config_hash}:{stage}")

    def _path(self, key: str) -> Path:
        return self.cache_dir / f"{key}.json"

    def get(self, key: str) -> Any | None:
        if not self.enabled:
            self.misses += 1
            return None
        path = self._path(key)
        if not path.exists():
            self.misses += 1
            return None
        self.hits += 1
        return read_json(path)

    def put(self, key: str, value: Any) -> None:
        if not self.enabled:
            return
        payload = value
        if isinstance(value, str):
            payload = {"value": value}
        write_json_atomic(self._path(key), payload)

    def put_stable(self, key: str, value: Any) -> None:
        if not self.enabled:
            return
        write_json_atomic(self._path(key), value)

    def hash_payload(self, value: Any) -> str:
        return sha256_text(stable_json_dumps(value))

