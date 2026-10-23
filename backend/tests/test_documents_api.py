"""US-101 Upload PDF, US-103 (từ chối file không phải PDF), US-104 danh sách — T1.2."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.app import create_app
from app.container import Container
from tests.conftest import documents_by_name, process_all, upload
from tests.pdfs import make_pdf


def test_ac_101_1_upload_one_pdf_shows_processing_immediately(client: TestClient) -> None:
    [result] = upload(client, ("hop_dong.pdf", make_pdf(["Contract text"])))

    assert result["documentId"]
    assert result["error"] is None
    doc = documents_by_name(client)["hop_dong.pdf"]
    assert doc["status"] == "PROCESSING"
    assert doc["id"] == result["documentId"]


def test_ac_101_2_status_becomes_ready_after_processing(client: TestClient, container: Container) -> None:
    upload(client, ("bao_cao.pdf", make_pdf(["Quarter report revenue", "Second page"])))

    process_all(container)

    doc = documents_by_name(client)["bao_cao.pdf"]
    assert doc["status"] == "READY"
    assert doc["pageCount"] == 2


def test_ac_101_3_multiple_files_get_independent_results(client: TestClient) -> None:
    results = upload(
        client,
        ("a.pdf", make_pdf(["A"])),
        ("ghi_chu.txt", b"plain text, not a pdf"),
        ("b.pdf", make_pdf(["B"])),
    )

    by_name = {r["fileName"]: r for r in results}
    assert by_name["a.pdf"]["documentId"] and by_name["b.pdf"]["documentId"]
    assert by_name["ghi_chu.txt"]["documentId"] is None
    assert by_name["ghi_chu.txt"]["error"] == {"code": "NOT_A_PDF", "message": "Chỉ hỗ trợ file PDF."}
    assert set(documents_by_name(client)) == {"a.pdf", "b.pdf"}


def test_ac_103_2_png_renamed_to_pdf_is_rejected_by_content(client: TestClient) -> None:
    png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32

    [result] = upload(client, ("anh.pdf", png))

    assert result["error"]["code"] == "NOT_A_PDF"  # type: ignore[index]
    assert documents_by_name(client) == {}


def test_no_orphan_file_when_database_write_fails(container: Container, monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(*_: object) -> None:
        raise RuntimeError("db down")

    monkeypatch.setattr(container.documents._repo, "add_with_job", boom)
    client = TestClient(create_app(container=container), raise_server_exceptions=False)

    resp = client.post("/api/v1/documents", files=[("files", ("x.pdf", make_pdf(["x"]), "application/pdf"))])

    assert resp.status_code == 500
    assert resp.json()["error"]["code"] == "INTERNAL_ERROR"
    files_dir: Path = container.settings.file_store_dir
    assert list(files_dir.iterdir()) == []
