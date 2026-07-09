"""Shared Pydantic schemas."""

from datetime import datetime
from typing import Any, Generic, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseSchema):
    message: str


class ErrorResponse(BaseModel):
    detail: str
    code: str = "ERROR"
    request_id: Optional[str] = None
    details: Optional[dict[str, Any]] = None


class PaginationMeta(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int


class PaginatedResult(BaseModel, Generic[T]):
    items: list[T]
    meta: PaginationMeta


class CitationSchema(BaseModel):
    document_id: Optional[UUID] = None
    document_title: str
    page_number: Optional[int] = None
    section: Optional[str] = None
    chunk_id: Optional[str] = None
    relevance_score: Optional[float] = None
    excerpt: Optional[str] = None
    embedding: Optional[list[float]] = None


class TimestampSchema(BaseSchema):
    created_at: datetime
    updated_at: Optional[datetime] = None
