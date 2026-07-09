"""Message document."""

from datetime import datetime
from typing import Any
from uuid import UUID

from beanie import Document
from pydantic import Field
from pymongo import ASCENDING, IndexModel

from app.models.base import new_uuid, utcnow
from app.models.enums import MessageRole


class Message(Document):
    id: UUID = Field(default_factory=new_uuid)
    conversation_id: UUID
    role: MessageRole
    content: str
    citations: list[dict[str, Any]] | None = None
    token_count: int | None = None
    created_at: datetime = Field(default_factory=utcnow)

    class Settings:
        name = "messages"
        indexes = [
            IndexModel([("conversation_id", ASCENDING)]),
            IndexModel([("created_at", ASCENDING)]),
        ]
