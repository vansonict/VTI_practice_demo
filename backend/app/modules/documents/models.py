from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class DocumentStatus(StrEnum):
    PROCESSING = "PROCESSING"
    READY = "READY"
    UNUSABLE = "UNUSABLE"


class UnusableReason(StrEnum):
    SCANNED = "scanned"
    PASSWORD = "password"  # noqa: S105 — lý do lỗi, không phải mật khẩu
    CORRUPT = "corrupt"
    PROCESSING_FAILED = "processing_failed"


@dataclass
class Document:
    id: str
    name: str
    size_bytes: int
    status: DocumentStatus
    content_hash: str
    file_ref: str
    uploaded_by: str
    uploaded_at: datetime
    page_count: int | None = None
    unusable_reason: UnusableReason | None = None
    retryable: bool = False


@dataclass(frozen=True)
class UploadedFile:
    name: str
    data: bytes


@dataclass(frozen=True)
class UploadResult:
    file_name: str
    document_id: str | None = None
    error_code: str | None = None
    error_message: str | None = None
