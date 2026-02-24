from llm_prep.chunking import chunk_text, split_paragraphs


def test_chunking_splits_on_boundaries() -> None:
    text = "HEADER:\n\n" + "A sentence. " * 120 + "\n\nSECOND:\n\n" + "B sentence. " * 120
    paragraphs = split_paragraphs(text)
    chunks = chunk_text(paragraphs, target_chars=500)
    assert len(chunks) >= 2
    assert all(chunk.strip() for chunk in chunks)


def test_chunking_no_empty_chunks() -> None:
    chunks = chunk_text(["   ", "content"], target_chars=1000)
    assert chunks == ["content"]

