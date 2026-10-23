"""REST API /api/v1 (SDD §3.6). Xác thực chưa có (T4.1): dùng người dùng dev cố định."""

from typing import Annotated

from fastapi import APIRouter, Depends, File, Request, UploadFile, status

from app.api.schemas import (
    CitationOut,
    ConversationOut,
    DocumentOut,
    ErrorResponse,
    MessageOut,
    QuestionIn,
    UploadError,
    UploadResultOut,
)
from app.container import Container
from app.modules.documents.models import UploadedFile

router = APIRouter(prefix="/api/v1", responses={422: {"model": ErrorResponse}})


def get_container(request: Request) -> Container:
    container: Container = request.app.state.container
    return container


ContainerDep = Annotated[Container, Depends(get_container)]


def current_user(c: ContainerDep) -> str:
    return c.settings.dev_user_id


UserDep = Annotated[str, Depends(current_user)]


@router.post(
    "/documents", status_code=status.HTTP_202_ACCEPTED, response_model=list[UploadResultOut], tags=["documents"]
)
async def upload_documents(
    c: ContainerDep, user: UserDep, files: Annotated[list[UploadFile], File(description="Một hoặc nhiều file PDF")]
) -> list[UploadResultOut]:
    uploaded = [UploadedFile(f.filename or "unnamed.pdf", await f.read()) for f in files]
    results = c.documents.upload(uploaded, user)
    return [
        UploadResultOut(
            file_name=r.file_name,
            document_id=r.document_id,
            error=UploadError(code=r.error_code, message=r.error_message or "") if r.error_code else None,
        )
        for r in results
    ]


@router.get("/documents", response_model=list[DocumentOut], tags=["documents"])
def list_documents(c: ContainerDep) -> list[DocumentOut]:
    return [
        DocumentOut(
            id=d.id,
            name=d.name,
            size_bytes=d.size_bytes,
            page_count=d.page_count,
            status=d.status.value,
            unusable_reason=d.unusable_reason.value if d.unusable_reason else None,
            retryable=d.retryable,
            uploaded_by=d.uploaded_by,
            uploaded_at=d.uploaded_at,
        )
        for d in c.documents.list_documents()
    ]


@router.post("/conversations", status_code=status.HTTP_201_CREATED, response_model=ConversationOut, tags=["qa"])
def create_conversation(c: ContainerDep, user: UserDep) -> ConversationOut:
    return ConversationOut(id=c.qa.start_conversation(user))


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=MessageOut,
    tags=["qa"],
    responses={
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
        504: {"model": ErrorResponse},
    },
)
def ask(conversation_id: str, body: QuestionIn, c: ContainerDep, user: UserDep) -> MessageOut:
    """NOT_FOUND (không có thông tin trong kho) là kết quả hợp lệ HTTP 200, không phải lỗi."""
    m = c.qa.ask(conversation_id, user, body.text)
    return MessageOut(
        id=m.id,
        conversation_id=m.conversation_id,
        kind=m.kind.value,
        text=m.text,
        error_type=m.error_type,
        citations=[
            CitationOut(
                document_id=x.document_id,
                document_name=x.document_name,
                page=x.page,
                document_deleted=x.document_deleted,
            )
            for x in m.citations
        ],
        created_at=m.created_at,
    )
