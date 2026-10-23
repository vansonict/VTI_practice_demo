from dataclasses import dataclass
from typing import Protocol

from app.modules.documents.models import UnusableReason


@dataclass(frozen=True)
class ClaimedJob:
    job_id: str
    document_id: str
    file_ref: str
    attempts: int


@dataclass(frozen=True)
class ChunkRecord:
    page: int
    ordinal: int
    text: str
    embedding: list[float]


class IngestionRepository(Protocol):
    def claim_next_job(self, lock_seconds: int) -> ClaimedJob | None:
        """Nhận một job QUEUED hoặc RUNNING đã quá hạn khóa; mỗi job chỉ một worker nhận được."""
        ...

    def complete(self, job: ClaimedJob, page_count: int, chunks: list[ChunkRecord]) -> bool:
        """Ghi chunks + READY + job DONE trong một giao dịch. Trả False nếu tài liệu đã bị xóa."""
        ...

    def fail(self, job: ClaimedJob, reason: UnusableReason, retryable: bool, error: str) -> None: ...
