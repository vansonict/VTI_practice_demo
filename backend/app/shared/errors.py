"""Mô hình lỗi chuẩn (SDD §3.6, OpenAPI `Error`)."""

from typing import Any


class AppError(Exception):
    """Lỗi nghiệp vụ có mã chuẩn; API chuyển thành `{ "error": { code, message, details, correlationId } }`."""

    def __init__(self, code: str, message: str, status: int, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status
        self.details = details


def not_found(resource: str) -> AppError:
    return AppError("NOT_FOUND_RESOURCE", f"Không tìm thấy {resource}.", 404)
