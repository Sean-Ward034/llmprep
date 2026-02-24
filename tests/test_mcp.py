from pathlib import Path

from llm_prep.mcp_server import llmprep_ingest, llmprep_validate


def test_mcp_tool_functions(tmp_path: Path) -> None:
    source = tmp_path / "src.txt"
    source.write_text("Please update integrations.", encoding="utf-8")
    out_dir = tmp_path / "out"

    ingest_result = llmprep_ingest(path=str(source), out_dir=str(out_dir), output_mode="file")
    assert "ragpack_dir" in ingest_result

    validate_result = llmprep_validate(ragpack_dir=str(out_dir / "ragpack"))
    assert validate_result["ok"] is True

