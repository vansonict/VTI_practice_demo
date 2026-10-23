"""PdfExtractor (ADR-003): trích văn bản theo trang; thư viện cụ thể nằm ở adapter."""

from typing import Protocol


class PdfPasswordProtected(Exception):
    pass


class PdfCorrupt(Exception):
    pass


class PdfExtractor(Protocol):
    def extract_pages(self, data: bytes) -> list[str]:
        """Trả văn bản từng trang (chỉ số 0 = trang 1). Ném PdfPasswordProtected hoặc PdfCorrupt."""
        ...
