"""Conversation document."""

from datetime import datetime
from typing import Any
from uuid import UUID

from beanie import Document
from pydantic import Field
from pymongo import ASCENDING, IndexModel

from app.models.base import new_uuid, utcnow


class Conversation(Document):
    id: UUID = Field(default_factory=new_uuid)
    user_id: UUID | None = None
    title: str | None = None
    is_archived: bool = False
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    # Populated at read time (not stored)
    messages: list[Any] = Field(default_factory=list, exclude=True)

    class Settings:
        name = "conversations"
        indexes = [
            IndexModel([("user_id", ASCENDING)]),
            IndexModel([("updated_at", ASCENDING)]),
        ]
