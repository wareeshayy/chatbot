"""Notification schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field, HttpUrl

from app.models.enums import NotificationType
from app.schemas.common import BaseSchema


class NotificationCreateRequest(BaseSchema):
    title: str = Field(min_length=3, max_length=500)
    content: str = Field(min_length=5)
    type: NotificationType
    link_url: Optional[str] = None
    document_id: Optional[UUID] = None
    expires_at: Optional[datetime] = None


class NotificationUpdateRequest(BaseSchema):
    title: Optional[str] = Field(default=None, min_length=3, max_length=500)
    content: Optional[str] = Field(default=None, min_length=5)
    type: Optional[NotificationType] = None
    link_url: Optional[str] = None
    document_id: Optional[UUID] = None
    is_published: Optional[bool] = None
    expires_at: Optional[datetime] = None


class NotificationResponse(BaseSchema):
    id: UUID
    title: str
    content: str
    type: NotificationType
    link_url: Optional[str] = None
    document_id: Optional[UUID] = None
    is_published: bool
    published_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
