"""Unit test: chia đoạn, embedding giả lập, cổng 2, health, mô hình lỗi, hợp đồng OpenAPI."""

from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from app.adapters.fake_embedding import FakeEmbedding
from app.modules.ingestion.chunker import chunk_pages
from app.modules.qa.models import MessageKind
from app.modules.qa.service import QaParams, QaService
from app.ports.llm import ComposedAnswer, ComposeStatus, Evidence, Turn

OPENAPI = Path(__file__).resolve().parents[2] / "docs" / "04-design" / "api" / "openapi.yaml"


def test_chunker_never_crosses_pages_and_overlaps_within_page() -> None:
    pages = [" ".join(f"a{i}" for i in range(25)), "", " ".join(f"c{i}" for i in range(5))]

    chunks = chunk_pages(pages, max_words=10, overlap_words=2)

    assert [c.page for c in chunks] == [1, 1, 1, 3]
    assert chunks[0].text.split()[-2:] == chunks[1].text.split()[:2]
    assert [c.ordinal for c in chunks] == [0, 1, 2, 3]


def test_chunker_rejects_bad_params() -> None:
    with pytest.raises(ValueError, match="max_words"):
        chunk_pages(["x"], max_words=5, overlap_words=5)


def test_fake_embedding_is_deterministic_normalized_and_lexical() -> None:
    e = FakeEmbedding(dim=64)
    a, b = e.embed_query("Điều khoản thanh toán"), e.embed_query("Điều khoản thanh toán")
    c = e.embed_query("hoàn toàn khác biệt")

    assert a == b and len(a) == 64
    assert abs(sum(x * x for x in a) - 1.0) < 1e-9
    assert sum(x * y for x, y in zip(a, b, strict=True)) > sum(x * y for x, y in zip(a, c, strict=True))


class _StubConversations:
    def owner_of(self, _: str) -> str:
        return "u"

    def add_user_message(self, *_: object) -> None:
        return None

    def add_assistant_message(
        self, conversation_id: str, kind: MessageKind, text: str | None, *_: object, **__: object
    ) -> MessageKind:
        return kind

    def create(self, _: str) -> str:
        return "c"


class _InsufficientLlm:
    def compose(self, question: str, evidence: list[Evidence], history: list[Turn]) -> ComposedAnswer:
        return ComposedAnswer(ComposeStatus.INSUFFICIENT_EVIDENCE)


class _OneDoc:
    def count_ready(self) -> int:
        return 1


class _Retrieval:
    def retrieve(self, _: str) -> list[Evidence]:
        return [Evidence("e1", "text", "d1", "doc.pdf", 1, score=0.9)]


def test_gate_2_insufficient_evidence_is_not_found() -> None:
    qa = QaService(_StubConversations(), _OneDoc(), _Retrieval(), _InsufficientLlm(), QaParams(1000, 0.2))  # type: ignore[arg-type]

    assert qa.ask("c", "u", "question") == MessageKind.NOT_FOUND


def test_health_and_ready(client: TestClient) -> None:
    assert client.get("/healthz").json() == {"status": "ok"}
    assert client.get("/readyz").status_code == 200


def test_every_response_has_correlation_id_and_errors_use_standard_body(client: TestClient) -> None:
    resp = client.post("/api/v1/conversations/x/messages", json={})

    assert resp.status_code == 422
    body = resp.json()["error"]
    assert body["code"] == "VALIDATION_ERROR"
    assert body["correlationId"] == resp.headers["X-Correlation-Id"]


@pytest.mark.parametrize(
    ("method", "path", "body", "status", "code"),
    [
        ("post", "/api/v1/conversations/x/messages", b'{"text": "\xff\xfe"}', 400, "BAD_REQUEST"),
        ("get", "/api/v1/khong-ton-tai", None, 404, "NOT_FOUND_RESOURCE"),
        ("delete", "/api/v1/conversations", None, 405, "METHOD_NOT_ALLOWED"),
    ],
)
def test_framework_errors_also_use_standard_error_body(
    client: TestClient, method: str, path: str, body: bytes | None, status: int, code: str
) -> None:
    resp = client.request(method, path, content=body, headers={"Content-Type": "application/json"})

    assert resp.status_code == status
    assert resp.json()["error"]["code"] == code
    assert resp.json()["error"]["correlationId"]


def test_implementation_covers_every_operation_in_design_openapi(client: TestClient) -> None:
    design = yaml.safe_load(OPENAPI.read_text(encoding="utf-8"))
    actual = client.get("/openapi.json").json()["paths"]

    missing = [
        f"{method.upper()} {path}"
        for path, ops in design["paths"].items()
        for method in ops
        if method not in actual.get(path.replace("{conversationId}", "{conversation_id}"), {})
    ]
    assert missing == []
