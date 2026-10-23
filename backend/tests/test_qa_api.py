"""US-201 hỏi, US-202/204 chỉ từ kho + không tìm thấy, US-203 trích dẫn — T1.5 (các cổng cơ bản của T3.2)."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import update
from sqlalchemy.orm import Session

from app.adapters.fake_llm import FakeLlm
from app.api.app import create_app
from app.config import Settings
from app.container import Container, build_container
from app.db.tables import DocumentRow
from tests.conftest import process_all, upload
from tests.pdfs import make_pdf

CONTRACT = [
    "Service contract between Company A and Company B. Duration is twenty four months.",
    "Scope of work includes deployment training and support.",
    "Payment terms: the customer pays within thirty days after receiving the invoice. Late payment interest applies.",
]


def _ready_library(client: TestClient, container: Container) -> None:
    upload(client, ("hop_dong_A.pdf", make_pdf(CONTRACT)))
    process_all(container)


def _ask(client: TestClient, text: str) -> tuple[int, dict[str, object]]:
    cid = client.post("/api/v1/conversations").json()["id"]
    resp = client.post(f"/api/v1/conversations/{cid}/messages", json={"text": text})
    return resp.status_code, resp.json()


def test_ac_201_1_and_203_1_answer_cites_document_name_and_page(client: TestClient, container: Container) -> None:
    _ready_library(client, container)

    status, msg = _ask(client, "What are the payment terms for the invoice?")

    assert status == 200
    assert msg["kind"] == "ANSWER"
    assert "thirty days" in str(msg["text"])
    assert msg["citations"] == [
        {
            "documentId": msg["citations"][0]["documentId"],
            "documentName": "hop_dong_A.pdf",
            "page": 3,
            "documentDeleted": False,
        }  # type: ignore[index]
    ]


def test_ac_204_1_out_of_scope_question_is_not_found_without_calling_llm(
    client: TestClient, container: Container
) -> None:
    _ready_library(client, container)
    assert isinstance(container.llm, FakeLlm)
    calls_before = container.llm.calls

    status, msg = _ask(client, "Thu do nuoc Phap la gi")

    assert status == 200
    assert msg["kind"] == "NOT_FOUND"
    assert msg["text"] is None and msg["citations"] == []
    assert container.llm.calls == calls_before  # cổng 1: không gọi LLM


def test_ac_103_3_unusable_document_is_never_cited(client: TestClient, container: Container) -> None:
    _ready_library(client, container)
    with Session(container.engine) as s, s.begin():
        s.execute(update(DocumentRow).values(status="UNUSABLE", unusable_reason="processing_failed"))
    upload(client, ("other.pdf", make_pdf(["Unrelated marketing brochure about coffee machines"])))
    process_all(container)

    _, msg = _ask(client, "What are the payment terms for the invoice?")

    assert all(c["documentName"] != "hop_dong_A.pdf" for c in msg["citations"])  # type: ignore[union-attr]


def test_no_ready_documents_returns_409(client: TestClient) -> None:
    status, body = _ask(client, "Anything?")

    assert status == 409
    assert body["error"]["code"] == "NO_READY_DOCUMENTS"  # type: ignore[index]


@pytest.mark.parametrize(("text", "code"), [("   ", "QUESTION_EMPTY"), ("x" * 1001, "QUESTION_TOO_LONG")])
def test_invalid_question_returns_422(client: TestClient, container: Container, text: str, code: str) -> None:
    _ready_library(client, container)

    status, body = _ask(client, text)

    assert status == 422
    assert body["error"]["code"] == code  # type: ignore[index]


def test_unknown_conversation_returns_404(client: TestClient) -> None:
    resp = client.post("/api/v1/conversations/does-not-exist/messages", json={"text": "hi"})

    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "NOT_FOUND_RESOURCE"


@pytest.mark.parametrize(
    ("mode", "status", "code"),
    [("timeout", 504, "AI_TIMEOUT"), ("quota", 503, "AI_QUOTA"), ("unavailable", 503, "AI_UNAVAILABLE")],
)
def test_ai_failure_is_an_error_never_not_found(settings: Settings, mode: str, status: int, code: str) -> None:
    container = build_container(settings, llm=FakeLlm(mode))
    with TestClient(create_app(container=container)) as client:
        _ready_library(client, container)

        got_status, body = _ask(client, "What are the payment terms for the invoice?")

    assert got_status == status
    assert body["error"]["code"] == code  # type: ignore[index]
    assert body["error"]["correlationId"]  # type: ignore[index]


def test_citation_to_unknown_evidence_is_dropped_and_becomes_not_found(settings: Settings) -> None:
    container = build_container(settings, llm=FakeLlm("cite_unknown_evidence"))
    with TestClient(create_app(container=container)) as client:
        _ready_library(client, container)

        status, msg = _ask(client, "What are the payment terms for the invoice?")

    assert status == 200
    assert msg["kind"] == "NOT_FOUND"
