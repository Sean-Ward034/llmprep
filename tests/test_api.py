from pathlib import Path

from fastapi.testclient import TestClient

from llm_prep.api import create_app


def test_api_health() -> None:
    client = TestClient(create_app())
    response = client.get("/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_api_ingest_and_inline_cap(tmp_path: Path) -> None:
    source = tmp_path / "source.txt"
    source.write_text("Need to deliver release notes.", encoding="utf-8")
    out_dir = tmp_path / "out"

    client = TestClient(create_app())
    ingest_resp = client.post(
        "/v1/ingest",
        json={
            "path": str(source),
            "out_dir": str(out_dir),
            "output_mode": "file",
        },
    )
    assert ingest_resp.status_code == 200
    assert "ragpack_dir" in ingest_resp.json()

    cap_resp = client.post(
        "/v1/ingest",
        json={
            "path": str(source),
            "out_dir": str(tmp_path / "out_inline"),
            "output_mode": "inline",
            "inline_max_bytes": 50,
        },
    )
    assert cap_resp.status_code == 413

