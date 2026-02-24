from pathlib import Path

from llm_prep.ingest.html_ingest import ingest_html


def test_html_ingest_extracts_text_and_tables() -> None:
    fixture = Path("tests/fixtures/sample.html")
    parsed = ingest_html(fixture, {})
    assert parsed["text_segments"]
    assert len(parsed["tables"]) == 1
    table = parsed["tables"][0]
    assert table["table_kind"] == "html_table"
    assert table["metadata"]["html_table_index"] == 1

