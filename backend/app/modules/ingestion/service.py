"""Xử lý một job tài liệu (T1.3; phân loại lỗi tối thiểu theo SDD A1 — retry/timeout đầy đủ thuộc T2.2)."""

import logging
import time
from dataclasses import dataclass

from app.modules.documents.models import UnusableReason
from app.modules.ingestion.chunker import chunk_pages
from app.modules.ingestion.repository import ChunkRecord, ClaimedJob, IngestionRepository
from app.ports.embedding import EmbeddingPort
from app.ports.filestore import FileStorePort
from app.ports.pdf import PdfCorrupt, PdfExtractor, PdfPasswordProtected

logger = logging.getLogger(__name__)

EMBED_BATCH = 32  # [Initial]


@dataclass(frozen=True)
class IngestionParams:
    chunk_max_words: int
    chunk_overlap_words: int
    job_lock_seconds: int
    scanned_text_ratio: float


class IngestionService:
    def __init__(
        self,
        repo: IngestionRepository,
        files: FileStorePort,
        extractor: PdfExtractor,
        embedding: EmbeddingPort,
        params: IngestionParams,
    ) -> None:
        self._repo = repo
        self._files = files
        self._extractor = extractor
        self._embedding = embedding
        self._params = params

    def process_next(self) -> bool:
        """Xử lý tối đa một job. Trả True nếu có job được nhận."""
        job = self._repo.claim_next_job(self._params.job_lock_seconds)
        if job is None:
            return False
        started = time.perf_counter()
        try:
            self._process(job)
        except PdfPasswordProtected:
            self._repo.fail(job, UnusableReason.PASSWORD, retryable=False, error="password protected")
        except PdfCorrupt as exc:
            self._repo.fail(job, UnusableReason.CORRUPT, retryable=False, error=type(exc).__name__)
        except _Scanned:
            self._repo.fail(job, UnusableReason.SCANNED, retryable=False, error="no text layer")
        except Exception as exc:
            # Lỗi tạm thời (embedding, lưu trữ…): cho phép thử lại (T2.3). Không log nội dung tài liệu.
            logger.exception("ingestion_failed", extra={"document_id": job.document_id})
            self._repo.fail(job, UnusableReason.PROCESSING_FAILED, retryable=True, error=type(exc).__name__)
        logger.info(
            "ingestion_job_finished",
            extra={"document_id": job.document_id, "seconds": round(time.perf_counter() - started, 3)},
        )
        return True

    def _process(self, job: ClaimedJob) -> None:
        pages = self._extractor.extract_pages(self._files.read(job.file_ref))
        if not pages:
            raise PdfCorrupt("0 pages")
        with_text = sum(1 for p in pages if p.strip())
        if with_text / len(pages) < self._params.scanned_text_ratio:
            raise _Scanned()
        drafts = chunk_pages(pages, self._params.chunk_max_words, self._params.chunk_overlap_words)
        vectors: list[list[float]] = []
        for i in range(0, len(drafts), EMBED_BATCH):
            vectors.extend(self._embedding.embed_passages([d.text for d in drafts[i : i + EMBED_BATCH]]))
        records = [ChunkRecord(d.page, d.ordinal, d.text, v) for d, v in zip(drafts, vectors, strict=True)]
        if not self._repo.complete(job, page_count=len(pages), chunks=records):
            logger.info("ingestion_discarded_deleted_document", extra={"document_id": job.document_id})


class _Scanned(Exception):
    pass
