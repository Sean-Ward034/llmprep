from datetime import datetime, timezone
from pathlib import Path
import shutil

from llm_prep.config import build_config
from llm_prep.service import ingest


def _copy_fixture(name: str, dst: Path) -> None:
    src = Path("tests/fixtures") / name
    shutil.copy2(src, dst / name)


def test_ingest_deterministic_with_fixed_time(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    out_dir = tmp_path / "out"
    input_dir.mkdir()
    _copy_fixture("sample.csv", input_dir)
    _copy_fixture("sample.html", input_dir)
    _copy_fixture("sample.txt", input_dir)

    config, cfg_hash, _ = build_config()
    fixed_time = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)

    ingest(
        source_path=input_dir,
        out_dir=out_dir,
        config=config,
        config_hash=cfg_hash,
        deterministic_time=fixed_time,
    )
    first_bytes = {
        p.name: p.read_bytes()
        for p in (out_dir / "ragpack").iterdir()
        if p.is_file()
    }

    ingest(
        source_path=input_dir,
        out_dir=out_dir,
        config=config,
        config_hash=cfg_hash,
        force=True,
        deterministic_time=fixed_time,
    )
    second_bytes = {
        p.name: p.read_bytes()
        for p in (out_dir / "ragpack").iterdir()
        if p.is_file()
    }

    assert first_bytes == second_bytes

