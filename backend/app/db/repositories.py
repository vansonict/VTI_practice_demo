"""Hiện thực repository bằng SQLAlchemy. Mỗi phương thức là một giao dịch."""

from datetime import timedelta

import numpy as np
from sqlalchemy import func, or_, select, update
from sqlalchemy.orm import Session, sessionmaker

from app.db.tables import ChunkRow, CitationRow, ConversationRow, DocumentRow, MessageRow, ProcessingJobRow
from app.modules.documents.models import Document, DocumentStatus, UnusableReason
from app.modules.ingestion.repository import ChunkRecord, ClaimedJob
from app.modules.qa.models import AssistantMessage, Citation, MessageKind
from app.ports.llm import Evidence
from app.shared.ids import new_id, utcnow


def _to_document(r: DocumentRow) -> Document:
    return Document(
        id=r.id,
        name=r.name,
        size_bytes=r.size_bytes,
        status=DocumentStatus(r.status),
        content_hash=r.content_hash,
        file_ref=r.file_ref,
        uploaded_by=r.uploaded_by,
        uploaded_at=r.uploaded_at,
        page_count=r.page_count,
        unusable_reason=UnusableReason(r.unusable_reason) if r.unusable_reason else None,
        retryable=r.retryable,
    )


class SqlDocumentRepository:
    def __init__(self, sf: sessionmaker[Session]) -> None:
        self._sf = sf

    def add_with_job(self, document: Document) -> None:
        now = utcnow()
        with self._sf.begin() as s:
            s.add(
                DocumentRow(
                    id=document.id,
                    name=document.name,
                    size_bytes=document.size_bytes,
                    page_count=None,
                    status=document.status.value,
                    unusable_reason=None,
                    retryable=False,
                    content_hash=document.content_hash,
                    file_ref=document.file_ref,
                    uploaded_by=document.uploaded_by,
                    uploaded_at=document.uploaded_at,
                )
            )
            s.flush()
            s.add(
                ProcessingJobRow(
                    id=new_id(), document_id=document.id, state="QUEUED", attempts=0, created_at=now, updated_at=now
                )
            )

    def list_all(self) -> list[Document]:
        with self._sf() as s:
            return [_to_document(r) for r in s.scalars(select(DocumentRow).order_by(DocumentRow.uploaded_at))]

    def count_ready(self) -> int:
        with self._sf() as s:
            return int(s.scalar(select(func.count()).where(DocumentRow.status == DocumentStatus.READY.value)) or 0)


class SqlIngestionRepository:
    def __init__(self, sf: sessionmaker[Session]) -> None:
        self._sf = sf

    def claim_next_job(self, lock_seconds: int) -> ClaimedJob | None:
        now = utcnow()
        with self._sf.begin() as s:
            # SQLite tuần tự hóa ghi; PostgreSQL sẽ dùng FOR UPDATE SKIP LOCKED (ADR-001, ADR-006)
            candidates = s.scalars(
                select(ProcessingJobRow)
                .where(
                    or_(
                        ProcessingJobRow.state == "QUEUED",
                        (ProcessingJobRow.state == "RUNNING") & (ProcessingJobRow.locked_until < now),
                    )
                )
                .order_by(ProcessingJobRow.created_at)
                .limit(5)
            ).all()
            for job in candidates:
                # Đọc giá trị trước khi UPDATE: ORM tự đồng bộ object trong session sau lệnh UPDATE
                job_id, document_id, attempts = job.id, job.document_id, job.attempts + 1
                lock_cond = (
                    ProcessingJobRow.locked_until.is_(None)
                    if job.locked_until is None
                    else ProcessingJobRow.locked_until == job.locked_until
                )
                claimed = s.execute(
                    update(ProcessingJobRow)
                    .where(ProcessingJobRow.id == job_id, ProcessingJobRow.state == job.state, lock_cond)
                    .values(
                        state="RUNNING",
                        attempts=attempts,
                        locked_until=now + timedelta(seconds=lock_seconds),
                        updated_at=now,
                    )
                    .execution_options(synchronize_session=False)
                )
                if claimed.rowcount == 1:  # type: ignore[attr-defined]
                    doc = s.get(DocumentRow, document_id)
                    if doc is None:
                        continue
                    return ClaimedJob(job_id, document_id, doc.file_ref, attempts)
        return None

    def complete(self, job: ClaimedJob, page_count: int, chunks: list[ChunkRecord]) -> bool:
        now = utcnow()
        with self._sf.begin() as s:
            doc = s.get(DocumentRow, job.document_id)
            if doc is None:
                return False
            s.add_all(
                ChunkRow(
                    id=new_id(),
                    document_id=job.document_id,
                    page=c.page,
                    ordinal=c.ordinal,
                    text=c.text,
                    embedding=np.asarray(c.embedding, dtype=np.float32).tobytes(),
                )
                for c in chunks
            )
            doc.status = DocumentStatus.READY.value
            doc.page_count = page_count
            doc.unusable_reason = None
            doc.retryable = False
            s.execute(
                update(ProcessingJobRow).where(ProcessingJobRow.id == job.job_id).values(state="DONE", updated_at=now)
            )
        return True

    def fail(self, job: ClaimedJob, reason: UnusableReason, retryable: bool, error: str) -> None:
        now = utcnow()
        with self._sf.begin() as s:
            doc = s.get(DocumentRow, job.document_id)
            if doc is not None:
                doc.status = DocumentStatus.UNUSABLE.value
                doc.unusable_reason = reason.value
                doc.retryable = retryable
            s.execute(
                update(ProcessingJobRow)
                .where(ProcessingJobRow.id == job.job_id)
                .values(state="FAILED", last_error=error[:256], updated_at=now)
            )


class SqlChunkSearchRepository:
    """Tìm cosine bằng numpy trên toàn bộ đoạn của tài liệu READY (tạm thời, ADR-006)."""

    def __init__(self, sf: sessionmaker[Session]) -> None:
        self._sf = sf

    def search(self, query_vector: list[float], k: int) -> list[Evidence]:
        with self._sf() as s:
            rows = s.execute(
                select(ChunkRow.id, ChunkRow.text, ChunkRow.page, ChunkRow.embedding, DocumentRow.id, DocumentRow.name)
                .join(DocumentRow, DocumentRow.id == ChunkRow.document_id)
                .where(DocumentRow.status == DocumentStatus.READY.value)
            ).all()
        if not rows:
            return []
        matrix = np.vstack([np.frombuffer(r[3], dtype=np.float32) for r in rows])
        q = np.asarray(query_vector, dtype=np.float32)
        norms = np.linalg.norm(matrix, axis=1) * (np.linalg.norm(q) or 1.0)
        scores = (matrix @ q) / np.where(norms == 0, 1.0, norms)
        order = np.argsort(-scores)[:k]
        return [
            Evidence(
                evidence_id=rows[i][0],
                text=rows[i][1],
                page=rows[i][2],
                document_id=rows[i][4],
                document_name=rows[i][5],
                score=float(scores[i]),
            )
            for i in order
        ]


class SqlConversationRepository:
    def __init__(self, sf: sessionmaker[Session]) -> None:
        self._sf = sf

    def create(self, user_id: str) -> str:
        cid = new_id()
        with self._sf.begin() as s:
            s.add(ConversationRow(id=cid, user_id=user_id, started_at=utcnow()))
        return cid

    def owner_of(self, conversation_id: str) -> str | None:
        with self._sf() as s:
            row = s.get(ConversationRow, conversation_id)
            return row.user_id if row else None

    def add_user_message(self, conversation_id: str, text: str) -> None:
        with self._sf.begin() as s:
            s.add(MessageRow(id=new_id(), conversation_id=conversation_id, role="USER", text=text, created_at=utcnow()))

    def add_assistant_message(
        self,
        conversation_id: str,
        kind: MessageKind,
        text: str | None,
        latency_ms: int,
        citations: list[Citation],
        error_type: str | None = None,
    ) -> AssistantMessage:
        mid, now = new_id(), utcnow()
        with self._sf.begin() as s:
            s.add(
                MessageRow(
                    id=mid,
                    conversation_id=conversation_id,
                    role="ASSISTANT",
                    kind=kind.value,
                    text=text,
                    error_type=error_type,
                    latency_ms=latency_ms,
                    created_at=now,
                )
            )
            s.flush()
            s.add_all(
                CitationRow(
                    id=new_id(),
                    message_id=mid,
                    chunk_id=c.chunk_id,
                    document_id=c.document_id,
                    document_name=c.document_name,
                    page=c.page,
                    position=i,
                )
                for i, c in enumerate(citations)
            )
        return AssistantMessage(mid, conversation_id, kind, now, text, error_type, latency_ms, citations)
