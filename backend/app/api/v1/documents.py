"""Document / knowledge base API routes."""

import uuid
from typing import Annotated, Any, Optional

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile

from app.dependencies import get_current_admin
from app.models.enums import DocumentCategory, DocumentStatus
from app.models.user import User
from app.schemas.common import MessageResponse, PaginatedResult, PaginationMeta
from app.schemas.document import DocumentDetailResponse, DocumentResponse, DocumentUpdateRequest
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["Documents"])


def _to_document_response(doc) -> DocumentResponse:
    return DocumentResponse(
        id=doc.id,
        title=doc.title,
        filename=doc.filename,
        file_type=doc.file_type,
        file_size_bytes=doc.file_size_bytes,
        category=doc.category,
        status=doc.status,
        version=doc.version,
        metadata=doc.doc_metadata,
        uploaded_by=doc.uploaded_by,
        chunk_count=doc.chunk_count,
        error_message=doc.error_message,
        indexed_at=doc.indexed_at,
        is_active=doc.is_active,
        created_at=doc.created_at,
        updated_at=doc.updated_at)


@router.post("/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(admin: Annotated[User, Depends(get_current_admin)],
    file: UploadFile = File(...),
    title: str = Form(...),
    category: DocumentCategory = Form(...),
    metadata: Optional[str] = Form(default=None)) -> DocumentResponse:
    import json

    meta: Optional[dict[str, Any]] = None
    if metadata:
        meta = json.loads(metadata)

    service = DocumentService()
    document = await service.upload_document(file, title, category, admin, meta)
    return _to_document_response(document)


@router.get("", response_model=PaginatedResult[DocumentResponse])
async def list_documents(admin: Annotated[User, Depends(get_current_admin)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[DocumentCategory] = None,
    status: Optional[DocumentStatus] = None) -> PaginatedResult[DocumentResponse]:
    service = DocumentService()
    result = await service.list_documents(page, page_size, category, status)
    return PaginatedResult(
        items=[_to_document_response(d) for d in result.items],
        meta=PaginationMeta(
            total=result.total,
            page=result.page,
            page_size=result.page_size,
            total_pages=result.total_pages))


@router.get("/categories")
async def get_document_categories() -> list[dict]:
    service = DocumentService()
    return service.get_categories()


@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document(
    document_id: uuid.UUID, admin: Annotated[User, Depends(get_current_admin)]) -> DocumentDetailResponse:
    from app.schemas.document import DocumentChunkResponse

    service = DocumentService()
    document = await service.get_document(document_id, with_chunks=True)
    response = _to_document_response(document)
    return DocumentDetailResponse(
        **response.model_dump(),
        chunks=[DocumentChunkResponse.model_validate(c) for c in document.chunks])


@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: uuid.UUID,
    data: DocumentUpdateRequest, admin: Annotated[User, Depends(get_current_admin)]) -> DocumentResponse:
    service = DocumentService()
    document = await service.update_document(document_id, data)
    return _to_document_response(document)


@router.delete("/{document_id}", response_model=MessageResponse)
async def delete_document(
    document_id: uuid.UUID, admin: Annotated[User, Depends(get_current_admin)]) -> MessageResponse:
    service = DocumentService()
    await service.delete_document(document_id)
    return MessageResponse(message="Document deleted")


@router.post("/{document_id}/reindex", response_model=DocumentResponse)
async def reindex_document(
    document_id: uuid.UUID, admin: Annotated[User, Depends(get_current_admin)]) -> DocumentResponse:
    service = DocumentService()
    document = await service.reindex_document(document_id)
    return _to_document_response(document)
