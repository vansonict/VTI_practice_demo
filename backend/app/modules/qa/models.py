from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class MessageKind(StrEnum):
    ANSWER = "ANSWER"
    NOT_FOUND = "NOT_FOUND"
    ERROR = "ERROR"


@dataclass(frozen=True)
class Citation:
    document_id: str
    document_name: str
    page: int
    chunk_id: str | None = None
    document_deleted: bool = False


@dataclass(frozen=True)
class AssistantMessage:
    id: str
    conversation_id: str
    kind: MessageKind
    created_at: datetime
    text: str | None = None
    error_type: str | None = None
    latency_ms: int | None = None
    citations: list[Citation] = field(default_factory=list)
