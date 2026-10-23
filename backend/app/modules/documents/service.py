"""Upload và danh sách tài liệu (US-101, US-104; T1.2). Giới hạn kích thước/kho đầy thuộc T2.1."""

import hashlib
import logging

from app.modules.documents.models import Document, DocumentStatus, UploadedFile, UploadResult
from app.modules.documents.repository import DocumentRepository
from app.ports.filestore import FileStorePort
from app.shared.ids import new_id, utcnow

logger = logging.getLogger(__name__)

PDF_MAGIC = b"%PDF-"


class DocumentService:
    def __init__(self, repo: DocumentRepository, files: FileStorePort) -> None:
        self._repo = repo
        self._files = files

    def upload(self, files: list[UploadedFile], user_id: str) -> list[UploadResult]:
        """Mỗi file có kết quả riêng; một file lỗi không ảnh hưởng file khác (AC-101.3)."""
        return [self._upload_one(f, user_id) for f in files]

    def _upload_one(self, f: UploadedFile, user_id: str) -> UploadResult:
        # Kiểm theo nội dung, không chỉ đuôi file (T2.1, ADR-003)
        if not f.data.startswith(PDF_MAGIC):
            return UploadResult(f.name, error_code="NOT_A_PDF", error_message="Chỉ hỗ trợ file PDF.")
        file_ref = self._files.put(f.data)
        doc = Document(
            id=new_id(),
            name=f.name,
            size_bytes=len(f.data),
            status=DocumentStatus.PROCESSING,
            content_hash=hashlib.sha256(f.data).hexdigest(),
            file_ref=file_ref,
            uploaded_by=user_id,
            uploaded_at=utcnow(),
        )
        try:
            self._repo.add_with_job(doc)
        except Exception:
            # Không để tệp mồ côi khi giao dịch lỗi (T1.2)
            self._files.delete(file_ref)
            raise
        logger.info("document_upload_started", extra={"document_id": doc.id, "size_bytes": doc.size_bytes})
        return UploadResult(f.name, document_id=doc.id)

    def list_documents(self) -> list[Document]:
        return self._repo.list_all()
