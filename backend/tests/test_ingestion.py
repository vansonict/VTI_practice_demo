"""UC-03 xử lý tài liệu, US-103 phân loại tài liệu không dùng được — T1.3 (phân loại tối thiểu của T2.2)."""

from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.container import Container
from app.db.tables import ChunkRow, ProcessingJobRow
from app.shared.ids import utcnow
from tests.conftest import documents_by_name, process_all, upload
from tests.pdfs import make_blank_pdf, make_corrupt_pdf, make_encrypted_pdf, make_pdf


def _chunks(container: Container, document_id: str) -> list[ChunkRow]:
    with Session(container.engine) as s:
        return list(s.scalars(select(ChunkRow).where(ChunkRow.document_id == document_id)))


def test_text_pdf_ready_and_every_chunk_belongs_to_exactly_one_page(client: TestClient, container: Container) -> None:
    container.ingestion._params = container.ingestion._params.__class__(
        20, 2, 300, 0.5
    )  # đoạn nhỏ để có nhiều đoạn/trang
    pages = [" ".join(f"page{n}word{i}" for i in range(60)) for n in range(1, 11)]
    [r] = upload(client, ("ten_pages.pdf", make_pdf(pages)))

    process_all(container)

    doc = documents_by_name(client)["ten_pages.pdf"]
    assert doc["status"] == "READY" and doc["pageCount"] == 10
    chunks = _chunks(container, str(r["documentId"]))
    assert len(chunks) > 10
    for c in chunks:
        assert 1 <= c.page <= 10
        tokens = {w.split("word")[0] for w in c.text.split()}
        assert tokens == {f"page{c.page}"}, "đoạn không được chứa văn bản của trang khác"


def test_each_job_is_processed_exactly_once(client: TestClient, container: Container) -> None:
    upload(client, ("a.pdf", make_pdf(["alpha"])), ("b.pdf", make_pdf(["beta"])))

    assert container.ingestion.process_next() is True
    assert container.ingestion.process_next() is True
    assert container.ingestion.process_next() is False


@pytest.mark.parametrize(
    ("name", "data", "reason", "retryable"),
    [
        ("mat_khau.pdf", make_encrypted_pdf(["secret contract"]), "password", False),
        ("hong.pdf", make_corrupt_pdf(), "corrupt", False),
        ("scan.pdf", make_blank_pdf(3), "scanned", False),
    ],
)
def test_ac_103_1_unusable_documents_get_specific_reason(
    client: TestClient, container: Container, name: str, data: bytes, reason: str, retryable: bool
) -> None:
    [r] = upload(client, (name, data))

    process_all(container)

    doc = documents_by_name(client)[name]
    assert doc["status"] == "UNUSABLE"
    assert doc["unusableReason"] == reason
    assert doc["retryable"] is retryable
    assert _chunks(container, str(r["documentId"])) == []


def test_embedding_failure_leaves_no_chunks_and_is_retryable(
    client: TestClient, container: Container, monkeypatch: pytest.MonkeyPatch
) -> None:
    def boom(_: list[str]) -> list[list[float]]:
        raise RuntimeError("embedding down")

    monkeypatch.setattr(container.embedding, "embed_passages", boom)
    [r] = upload(client, ("x.pdf", make_pdf(["some text"])))

    process_all(container)

    doc = documents_by_name(client)["x.pdf"]
    assert (doc["status"], doc["unusableReason"], doc["retryable"]) == ("UNUSABLE", "processing_failed", True)
    assert _chunks(container, str(r["documentId"])) == []


def test_job_with_expired_lock_is_reclaimed(client: TestClient, container: Container) -> None:
    upload(client, ("x.pdf", make_pdf(["text"])))
    repo = container.ingestion._repo
    first = repo.claim_next_job(lock_seconds=300)
    assert first is not None
    assert repo.claim_next_job(lock_seconds=300) is None  # đang bị khóa

    with Session(container.engine) as s, s.begin():
        s.execute(update(ProcessingJobRow).values(locked_until=utcnow() - timedelta(seconds=1)))

    again = repo.claim_next_job(lock_seconds=300)
    assert again is not None and again.job_id == first.job_id and again.attempts == 2
