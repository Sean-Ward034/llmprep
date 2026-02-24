from pathlib import Path

from llm_prep.ingest.csv_ingest import ingest_csv


def test_csv_ingest_basic() -> None:
    fixture = Path("tests/fixtures/sample.csv")
    parsed = ingest_csv(fixture, {"csv_sample_rows": 10})
    assert parsed["parser"]["name"] == "csv_ingest"
    assert len(parsed["tables"]) == 1
    table = parsed["tables"][0]
    assert table["table_kind"] == "csv_table"
    assert table["headers"] == ["Name", "Score", "Active"]
    assert len(table["rows"]) == 3

