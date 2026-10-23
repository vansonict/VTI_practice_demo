from typing import Protocol

from app.modules.qa.models import AssistantMessage, Citation, MessageKind


class ConversationRepository(Protocol):
    def create(self, user_id: str) -> str: ...

    def owner_of(self, conversation_id: str) -> str | None: ...

    def add_user_message(self, conversation_id: str, text: str) -> None: ...

    def add_assistant_message(
        self,
        conversation_id: str,
        kind: MessageKind,
        text: str | None,
        latency_ms: int,
        citations: list[Citation],
        error_type: str | None = None,
    ) -> AssistantMessage: ...


class ReadyDocumentCounter(Protocol):
    def count_ready(self) -> int: ...
