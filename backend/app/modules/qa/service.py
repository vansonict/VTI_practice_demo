"""Hỏi đáp có căn cứ (US-201, 202, 203, 204; T1.5).

Ba cổng "không tìm thấy" (SDD §3.8 A2):
  1. Không có bằng chứng hoặc điểm cao nhất < ngưỡng liên quan → NOT_FOUND, không gọi LLM.
  2. LLM trả INSUFFICIENT_EVIDENCE → NOT_FOUND.
  3. Trích dẫn không hợp lệ (mã bằng chứng lạ, claim không có mã) → bỏ claim; không còn claim → NOT_FOUND.
     (Thử lại một lần trước khi kết luận thuộc T3.2.)
Trích dẫn luôn do hệ thống dựng từ bản ghi bằng chứng (SDD D-06), không lấy từ văn bản mô hình trả.
Lỗi dịch vụ AI → ERROR, không bao giờ thành NOT_FOUND (SDD §3.7).
"""

import logging
import time
from dataclasses import dataclass

from app.modules.qa.models import AssistantMessage, Citation, MessageKind
from app.modules.qa.repository import ConversationRepository, ReadyDocumentCounter
from app.modules.retrieval.service import RetrievalService
from app.ports.llm import ComposeStatus, Evidence, LlmError, LlmPort, LlmQuotaExceeded, LlmTimeout
from app.shared.errors import AppError, not_found

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class QaParams:
    max_question_chars: int
    relevance_threshold: float


class QaService:
    def __init__(
        self,
        conversations: ConversationRepository,
        documents: ReadyDocumentCounter,
        retrieval: RetrievalService,
        llm: LlmPort,
        params: QaParams,
    ) -> None:
        self._conversations = conversations
        self._documents = documents
        self._retrieval = retrieval
        self._llm = llm
        self._params = params

    def start_conversation(self, user_id: str) -> str:
        return self._conversations.create(user_id)

    def ask(self, conversation_id: str, user_id: str, question: str) -> AssistantMessage:
        if self._conversations.owner_of(conversation_id) != user_id:
            raise not_found("cuộc trò chuyện")
        question = question.strip()
        if not question:
            raise AppError("QUESTION_EMPTY", "Câu hỏi không được để trống.", 422)
        if len(question) > self._params.max_question_chars:
            raise AppError(
                "QUESTION_TOO_LONG",
                f"Câu hỏi dài quá {self._params.max_question_chars} ký tự.",
                422,
                {"actual": len(question), "limit": self._params.max_question_chars},
            )
        if self._documents.count_ready() == 0:
            raise AppError("NO_READY_DOCUMENTS", "Chưa có tài liệu nào sẵn sàng truy vấn.", 409)

        started = time.perf_counter()
        self._conversations.add_user_message(conversation_id, question)

        def finish(
            kind: MessageKind, text: str | None, citations: list[Citation], error: str | None = None
        ) -> AssistantMessage:
            latency = int((time.perf_counter() - started) * 1000)
            logger.info(
                "answer_returned", extra={"kind": kind.value, "latency_ms": latency, "citations": len(citations)}
            )
            return self._conversations.add_assistant_message(conversation_id, kind, text, latency, citations, error)

        evidence = self._retrieval.retrieve(question)
        if not evidence or evidence[0].score < self._params.relevance_threshold:
            return finish(MessageKind.NOT_FOUND, None, [])  # cổng 1

        try:
            composed = self._llm.compose(question, evidence, history=[])
        except LlmError as exc:
            code, status = _ai_error(exc)
            finish(MessageKind.ERROR, None, [], error=code)
            raise AppError(
                code, "Hệ thống gặp lỗi khi trả lời. Đây không phải kết quả “không tìm thấy”.", status
            ) from exc

        if composed.status is ComposeStatus.INSUFFICIENT_EVIDENCE:
            return finish(MessageKind.NOT_FOUND, None, [])  # cổng 2

        by_id = {e.evidence_id: e for e in evidence}
        texts: list[str] = []
        citations: list[Citation] = []
        seen: set[tuple[str, int]] = set()
        for claim in composed.claims:
            cited = [by_id[i] for i in claim.evidence_ids if i in by_id]
            if not cited or len(cited) != len(claim.evidence_ids):
                continue  # cổng 3: claim không có trích dẫn hợp lệ thì không được hiển thị
            texts.append(claim.text)
            for ev in cited:
                if (ev.document_id, ev.page) not in seen:
                    seen.add((ev.document_id, ev.page))
                    citations.append(_citation(ev))
        if not texts:
            return finish(MessageKind.NOT_FOUND, None, [])  # cổng 3
        return finish(MessageKind.ANSWER, " ".join(texts), citations)


def _citation(ev: Evidence) -> Citation:
    return Citation(document_id=ev.document_id, document_name=ev.document_name, page=ev.page, chunk_id=ev.evidence_id)


def _ai_error(exc: LlmError) -> tuple[str, int]:
    if isinstance(exc, LlmTimeout):
        return "AI_TIMEOUT", 504
    if isinstance(exc, LlmQuotaExceeded):
        return "AI_QUOTA", 503
    return "AI_UNAVAILABLE", 503
