"""Notification document."""

from datetime import datetime
from uuid import UUID

from beanie import Document
from pydantic import Field

from app.models.base import new_uuid, utcnow
from app.models.enums import NotificationType


class Notification(Document):
    id: UUID = Field(default_factory=new_uuid)
    title: str
    content: str
    type: NotificationType
    link_url: str | None = None
    document_id: UUID | None = None
    is_published: bool = False
    published_at: datetime | None = None
    expires_at: datetime | None = None
    created_by: UUID | None = None
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

    class Settings:
        name = "notifications"
