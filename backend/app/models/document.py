"""Document and chunk documents."""

from datetime import datetime
from typing import Any
from uuid import UUID

from beanie import Document as BeanieDocument
from pydantic import Field
from pymongo import ASCENDING, IndexModel

from app.models.base import new_uuid, utcnow
from app.models.enums import DocumentCategory, DocumentStatus


class Document(BeanieDocument):
    id: UUID = Field(default_factory=new_uuid)
    title: str
    filename: str
    file_path: str
    file_type: str
    file_size_bytes: int
    category: DocumentCategory
    status: DocumentStatus = DocumentStatus.PENDING
    version: int = 1
    doc_metadata: dict[str, Any] | None = None
    uploaded_by: UUID | None = None
    chunk_count: int = 0
    error_message: str | None = None
    indexed_at: datetime | None = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    chunks: list[Any] = Field(default_factory=list, exclude=True)

    class Settings:
        name = "documents"
        indexes = [
            IndexModel([("category", ASCENDING)]),
            IndexModel([("status", ASCENDING)]),
            IndexModel([("is_active", ASCENDING)]),
        ]


class DocumentChunk(BeanieDocument):
    id: UUID = Field(default_factory=new_uuid)
    document_id: UUID
    chroma_id: str
    chunk_index: int
    content: str
    page_number: int | None = None
    section_title: str | None = None
    token_count: int | None = None
    chunk_metadata: dict[str, Any] | None = None
    embedding: list[float] | None = None
    created_at: datetime = Field(default_factory=utcnow)

    class Settings:
        name = "document_chunks"
        indexes = [
            IndexModel([("document_id", ASCENDING)]),
            IndexModel([("chroma_id", ASCENDING)], unique=True),
        ]
