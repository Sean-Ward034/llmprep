from datetime import datetime, timezone
from pathlib import Path

from llm_prep.config import build_config
from llm_prep.service import diff, ingest, validate


def test_diff_and_validate(tmp_path: Path) -> None:
    src1 = tmp_path / "src1"
    src2 = tmp_path / "src2"
    src1.mkdir()
    src2.mkdir()

    (src1 / "note.txt").write_text("Please update docs.\n", encoding="utf-8")
    (src2 / "note.txt").write_text("Please update docs.\nNeed to add tests.\n", encoding="utf-8")

    cfg, cfg_hash, _ = build_config()
    ts = datetime(2026, 1, 1, tzinfo=timezone.utc)
    out1 = tmp_path / "out1"
    out2 = tmp_path / "out2"

    ingest(source_path=src1, out_dir=out1, config=cfg, config_hash=cfg_hash, deterministic_time=ts)
    ingest(source_path=src2, out_dir=out2, config=cfg, config_hash=cfg_hash, deterministic_time=ts)

    diff_dir = tmp_path / "diff"
    summary = diff(old_ragpack=out1 / "ragpack", new_ragpack=out2 / "ragpack", out_dir=diff_dir)
    assert summary.chunks["changed"] >= 0

    result = validate(ragpack_dir=out2 / "ragpack")
    assert result.ok is True

