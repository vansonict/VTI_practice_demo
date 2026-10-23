"""LLM giả lập, xác định được (T1.1). Dùng cho dev và test khi chưa có nhà cung cấp được duyệt (OQ-009).

normal: không có bằng chứng → INSUFFICIENT_EVIDENCE; có → một claim là câu đầu của bằng chứng điểm cao nhất.
Các chế độ lỗi để test nhánh ERROR và cổng 3.
"""

import re

from app.ports.llm import (
    Claim,
    ComposedAnswer,
    ComposeStatus,
    Evidence,
    LlmInvalidOutput,
    LlmQuotaExceeded,
    LlmTimeout,
    LlmUnavailable,
    Turn,
)

MODES = {"normal", "timeout", "quota", "unavailable", "invalid_output", "cite_unknown_evidence"}


class FakeLlm:
    def __init__(self, mode: str = "normal") -> None:
        if mode not in MODES:
            raise ValueError(f"Chế độ LLM giả lập không hợp lệ: {mode}")
        self.mode = mode
        self.calls = 0

    def compose(self, question: str, evidence: list[Evidence], history: list[Turn]) -> ComposedAnswer:
        self.calls += 1
        if self.mode == "timeout":
            raise LlmTimeout()
        if self.mode == "quota":
            raise LlmQuotaExceeded()
        if self.mode == "unavailable":
            raise LlmUnavailable()
        if self.mode == "invalid_output":
            raise LlmInvalidOutput()
        if not evidence:
            return ComposedAnswer(ComposeStatus.INSUFFICIENT_EVIDENCE)
        top = evidence[0]
        evidence_id = "unknown-evidence" if self.mode == "cite_unknown_evidence" else top.evidence_id
        return ComposedAnswer(ComposeStatus.ANSWERED, [Claim(_first_sentence(top.text), [evidence_id])])


def _first_sentence(text: str) -> str:
    parts = re.split(r"(?<=[.!?])\s+", text.strip(), maxsplit=1)
    return parts[0]
