"""FastAPI app factory: middleware correlationId, mô hình lỗi chuẩn, health."""

import logging
import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import text
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routes import router
from app.config import Settings, get_settings
from app.container import Container, build_container
from app.shared.errors import AppError

logger = logging.getLogger(__name__)

_HTTP_CODES = {400: "BAD_REQUEST", 404: "NOT_FOUND_RESOURCE", 405: "METHOD_NOT_ALLOWED"}


def _error(
    request: Request, status: int, code: str, message: str, details: dict[str, object] | None = None
) -> JSONResponse:
    body = {
        "error": {"code": code, "message": message, "details": details, "correlationId": request.state.correlation_id}
    }
    return JSONResponse(body, status_code=status, headers={"X-Correlation-Id": request.state.correlation_id})


def create_app(settings: Settings | None = None, container: Container | None = None) -> FastAPI:
    app = FastAPI(title="Chat với tài liệu API", version="0.1.0")
    app.state.container = container or build_container(settings or get_settings())

    @app.middleware("http")
    async def correlation_id(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        request.state.correlation_id = uuid.uuid4().hex
        response = await call_next(request)
        response.headers["X-Correlation-Id"] = request.state.correlation_id
        return response

    @app.exception_handler(AppError)
    async def app_error(request: Request, exc: AppError) -> JSONResponse:
        return _error(request, exc.status, exc.code, exc.message, exc.details)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        return _error(
            request,
            422,
            "VALIDATION_ERROR",
            "Dữ liệu gửi lên không hợp lệ.",
            {"fields": [".".join(map(str, e["loc"])) for e in exc.errors()]},
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        # Lỗi do framework sinh (body JSON hỏng, route không tồn tại…) cũng phải theo mô hình lỗi chuẩn
        code = _HTTP_CODES.get(exc.status_code, "HTTP_ERROR")
        return _error(request, exc.status_code, code, str(exc.detail))

    @app.exception_handler(Exception)
    async def unexpected(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled_error", extra={"correlation_id": request.state.correlation_id})
        return _error(request, 500, "INTERNAL_ERROR", "Lỗi hệ thống.")

    @app.get("/healthz", tags=["ops"])
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/readyz", tags=["ops"])
    def readyz(request: Request) -> JSONResponse:
        """Kiểm CSDL; không gọi dịch vụ AI (SAD §4.3)."""
        try:
            with app.state.container.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except Exception:
            return _error(request, 503, "NOT_READY", "CSDL không sẵn sàng.")
        return JSONResponse({"status": "ready"})

    app.include_router(router)
    return app
