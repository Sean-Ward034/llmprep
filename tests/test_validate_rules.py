import json
from pathlib import Path

from llm_prep.service import validate


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_validate_flags_unknown_colors(tmp_path: Path) -> None:
    ragpack = tmp_path / "ragpack"
    ragpack.mkdir()
    _write_json(
        ragpack / "manifest.json",
        {"schema_version": "1.0.0", "tool_version": "0.1.0", "created_at": "2026-01-01T00:00:00Z", "config": {}, "sources": [], "stats": {}, "cache": {}},
    )
    (ragpack / "doc_chunks.jsonl").write_text("", encoding="utf-8")
    (ragpack / "tables.jsonl").write_text(
        json.dumps(
            {
                "table_id": "t1",
                "checksum": "x",
                "metadata": {"color_counts": {"UNKNOWN:indexed:64": 2}},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    _write_json(ragpack / "entities.json", {"schema_version": "1.0.0", "files": [], "headings": [], "key_values": [], "warnings": []})
    _write_json(ragpack / "task_spec.json", {"schema_version": "1.0.0", "tasks": []})
    _write_json(ragpack / "validation_report.json", {"schema_version": "1.0.0", "errors": [], "warnings": [], "metrics": {}, "timing_breakdown": {}})

    result = validate(ragpack_dir=ragpack)
    assert result.ok is False
    assert any("Unknown tiers/colors" in err for err in result.errors)

