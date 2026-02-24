from pathlib import Path

from llm_prep.normalize import normalize_text, sha256_file, stable_id


def test_stable_id_is_deterministic() -> None:
    a = stable_id(["one", "two", "three"])
    b = stable_id(["one", "two", "three"])
    assert a == b


def test_sha256_file_stable(tmp_path: Path) -> None:
    file_path = tmp_path / "sample.txt"
    file_path.write_text("hello\nworld\n", encoding="utf-8")
    assert sha256_file(file_path) == sha256_file(file_path)


def test_normalize_text_rules() -> None:
    text = "Line 1   \r\nLine\t2\r\n\r\n\r\nLine   3"
    normalized = normalize_text(text)
    assert normalized == "Line 1\nLine 2\n\nLine 3"

