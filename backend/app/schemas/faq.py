"""FAQ schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field

from app.schemas.common import BaseSchema


class FAQCreateRequest(BaseSchema):
    question: str = Field(min_length=5)
    answer: str = Field(min_length=5)
    category: Optional[str] = None
    display_order: int = 0
    is_published: bool = True


class FAQUpdateRequest(BaseSchema):
    question: Optional[str] = Field(default=None, min_length=5)
    answer: Optional[str] = Field(default=None, min_length=5)
    category: Optional[str] = None
    display_order: Optional[int] = None
    is_published: Optional[bool] = None


class FAQResponse(BaseSchema):
    id: UUID
    question: str
    answer: str
    category: Optional[str] = None
    display_order: int
    is_published: bool
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
