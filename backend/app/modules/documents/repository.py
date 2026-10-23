from typing import Protocol

from app.modules.documents.models import Document


class DocumentRepository(Protocol):
    def add_with_job(self, document: Document) -> None:
        """Tạo tài liệu PROCESSING và job QUEUED trong một giao dịch (T1.2)."""
        ...

    def list_all(self) -> list[Document]: ...

    def count_ready(self) -> int: ...
