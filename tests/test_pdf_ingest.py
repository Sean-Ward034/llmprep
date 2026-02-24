from pathlib import Path
from types import SimpleNamespace

import llm_prep.ingest.pdf_ingest as pdf_ingest


class _FakePDF:
    def __init__(self) -> None:
        self.pages = [SimpleNamespace(extract_text=lambda: "Report page one.")]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_pdf_ingest_with_mock(monkeypatch, tmp_path: Path) -> None:
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n%mock\n")

    monkeypatch.setattr(pdf_ingest.pdfplumber, "open", lambda _: _FakePDF())
    parsed = pdf_ingest.ingest_pdf(pdf_path, {})
    assert parsed["text_segments"]
    assert parsed["warnings"] == []

