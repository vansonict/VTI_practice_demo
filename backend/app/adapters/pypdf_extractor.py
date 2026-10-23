"""PdfExtractor dùng pypdf (ADR-003)."""

import io
import logging

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from app.ports.pdf import PdfCorrupt, PdfPasswordProtected

logging.getLogger("pypdf").setLevel(logging.ERROR)  # pypdf cảnh báo ồn với file hỏng; lỗi đã được phân loại


class PypdfExtractor:
    def extract_pages(self, data: bytes) -> list[str]:
        try:
            reader = PdfReader(io.BytesIO(data))
            if reader.is_encrypted:
                raise PdfPasswordProtected()
            return [page.extract_text() or "" for page in reader.pages]
        except PdfPasswordProtected:
            raise
        except PdfReadError as exc:
            raise PdfCorrupt(type(exc).__name__) from exc
        except Exception as exc:  # pypdf có thể ném nhiều loại lỗi với file hỏng; đều coi là hỏng
            raise PdfCorrupt(type(exc).__name__) from exc
