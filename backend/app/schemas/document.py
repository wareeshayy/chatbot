"""Document schemas."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import Field

from app.models.enums import DocumentCategory, DocumentStatus
from app.schemas.common import BaseSchema


class DocumentUpdateRequest(BaseSchema):
    title: Optional[str] = Field(default=None, max_length=500)
    category: Optional[DocumentCategory] = None
    metadata: Optional[dict[str, Any]] = None


class DocumentResponse(BaseSchema):
    id: UUID
    title: str
    filename: str
    file_type: str
    file_size_bytes: int
    category: DocumentCategory
    status: DocumentStatus
    version: int
    metadata: Optional[dict[str, Any]] = None
    uploaded_by: Optional[UUID] = None
    chunk_count: int
    error_message: Optional[str] = None
    indexed_at: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class DocumentChunkResponse(BaseSchema):
    id: UUID
    document_id: UUID
    chroma_id: str
    chunk_index: int
    content: str
    page_number: Optional[int] = None
    section_title: Optional[str] = None
    token_count: Optional[int] = None


class DocumentDetailResponse(DocumentResponse):
    chunks: list[DocumentChunkResponse] = []
