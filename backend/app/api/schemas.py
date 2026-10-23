"""Schema request/response, khớp docs/04-design/api/openapi.yaml (camelCase)."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class ApiModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class ErrorBody(ApiModel):
    code: str
    message: str
    details: dict[str, Any] | None = None
    correlation_id: str


class ErrorResponse(ApiModel):
    error: ErrorBody


class DocumentOut(ApiModel):
    id: str
    name: str
    size_bytes: int
    page_count: int | None
    status: str = Field(description="PROCESSING | READY | UNUSABLE")
    unusable_reason: str | None = Field(description="scanned | password | corrupt | processing_failed")
    retryable: bool
    uploaded_by: str
    uploaded_at: datetime


class UploadError(ApiModel):
    code: str
    message: str


class UploadResultOut(ApiModel):
    file_name: str
    document_id: str | None = None
    error: UploadError | None = None


class ConversationOut(ApiModel):
    id: str


class QuestionIn(ApiModel):
    text: str


class CitationOut(ApiModel):
    document_id: str
    document_name: str
    page: int
    document_deleted: bool = False


class MessageOut(ApiModel):
    id: str
    conversation_id: str
    role: str = "ASSISTANT"
    kind: str = Field(description="ANSWER | NOT_FOUND | ERROR")
    text: str | None
    error_type: str | None = None
    citations: list[CitationOut]
    created_at: datetime
