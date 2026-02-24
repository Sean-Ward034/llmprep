from pathlib import Path

from llm_prep.cache import CacheManager


def test_cache_hit_and_miss(tmp_path: Path) -> None:
    cache = CacheManager(tmp_path / ".cache")
    key = CacheManager.compose_key("abc", "1", "cfg", "parse")
    assert cache.get(key) is None
    assert cache.misses == 1
    cache.put_stable(key, {"ok": True})
    value = cache.get(key)
    assert value == {"ok": True}
    assert cache.hits == 1

