"""LlmPort (SDD §3.2, SAD §2.5 EI-1). Trích dẫn do hệ thống dựng từ evidenceIds (SDD D-06)."""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    text: str
    document_id: str
    document_name: str
    page: int
    score: float


@dataclass(frozen=True)
class Turn:
    role: str  # "user" | "assistant"
    text: str


class ComposeStatus(StrEnum):
    ANSWERED = "ANSWERED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


@dataclass(frozen=True)
class Claim:
    text: str
    evidence_ids: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ComposedAnswer:
    status: ComposeStatus
    claims: list[Claim] = field(default_factory=list)


class LlmError(Exception):
    """Lỗi chuẩn hóa từ dịch vụ AI; không bao giờ được hiểu là "không tìm thấy"."""


class LlmTimeout(LlmError):
    pass


class LlmQuotaExceeded(LlmError):
    pass


class LlmUnavailable(LlmError):
    pass


class LlmInvalidOutput(LlmError):
    pass


class LlmPort(Protocol):
    def compose(self, question: str, evidence: list[Evidence], history: list[Turn]) -> ComposedAnswer: ...
