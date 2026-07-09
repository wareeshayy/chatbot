"""FAQ document."""

from datetime import datetime
from uuid import UUID

from beanie import Document
from pydantic import Field

from app.models.base import new_uuid, utcnow


class FAQ(Document):
    id: UUID = Field(default_factory=new_uuid)
    question: str
    answer: str
    category: str | None = None
    display_order: int = 0
    is_published: bool = True
    created_by: UUID | None = None
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

    class Settings:
        name = "faqs"
