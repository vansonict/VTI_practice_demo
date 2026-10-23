"""Schema (SDD §3.5) — phần cần cho lát cắt đầu. Bảng users, feedback, analytics, audit thêm ở GĐ4."""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, LargeBinary, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class DocumentRow(Base):
    __tablename__ = "documents"
    __table_args__ = (
        CheckConstraint("status IN ('PROCESSING','READY','UNUSABLE')", name="ck_documents_status"),
        CheckConstraint(
            "unusable_reason IS NULL OR unusable_reason IN ('scanned','password','corrupt','processing_failed')",
            name="ck_documents_reason",
        ),
        Index("ix_documents_status", "status"),
    )

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(512))
    size_bytes: Mapped[int] = mapped_column(Integer)
    page_count: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(16))
    unusable_reason: Mapped[str | None] = mapped_column(String(32))
    retryable: Mapped[bool] = mapped_column(default=False)
    content_hash: Mapped[str] = mapped_column(String(64))
    file_ref: Mapped[str] = mapped_column(String(64))
    uploaded_by: Mapped[str] = mapped_column(String(64))
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ChunkRow(Base):
    __tablename__ = "chunks"
    __table_args__ = (Index("ix_chunks_document", "document_id"),)

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"))
    page: Mapped[int] = mapped_column(Integer)
    ordinal: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    embedding: Mapped[bytes] = mapped_column(LargeBinary)  # float32; PostgreSQL dùng vector(768) (ADR-004)


class ProcessingJobRow(Base):
    __tablename__ = "processing_jobs"
    __table_args__ = (
        CheckConstraint("state IN ('QUEUED','RUNNING','DONE','FAILED')", name="ck_jobs_state"),
        Index("ix_jobs_state_lock", "state", "locked_until"),
    )

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"))
    state: Mapped[str] = mapped_column(String(16))
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_error: Mapped[str | None] = mapped_column(String(256))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ConversationRow(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class MessageRow(Base):
    __tablename__ = "messages"
    __table_args__ = (
        CheckConstraint("role IN ('USER','ASSISTANT')", name="ck_messages_role"),
        CheckConstraint("kind IS NULL OR kind IN ('ANSWER','NOT_FOUND','ERROR')", name="ck_messages_kind"),
        Index("ix_messages_conversation", "conversation_id", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(16))
    kind: Mapped[str | None] = mapped_column(String(16))
    # Có lưu nội dung câu hỏi hay không chờ OQ-009; dev lưu để test
    text: Mapped[str | None] = mapped_column(Text)
    error_type: Mapped[str | None] = mapped_column(String(32))
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class CitationRow(Base):
    __tablename__ = "citations"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    message_id: Mapped[str] = mapped_column(ForeignKey("messages.id", ondelete="CASCADE"))
    # Trích dẫn cũ giữ tên và trang đã sao chép khi tài liệu bị xóa (SDD §3.5)
    chunk_id: Mapped[str | None] = mapped_column(ForeignKey("chunks.id", ondelete="SET NULL"))
    document_id: Mapped[str] = mapped_column(String(32))
    document_name: Mapped[str] = mapped_column(String(512))
    page: Mapped[int] = mapped_column(Integer)
    position: Mapped[int] = mapped_column(Integer)
