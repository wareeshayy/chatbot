"""Chat audit log document."""

from datetime import datetime
from typing import Any
from uuid import UUID

from beanie import Document
from pydantic import Field
from pymongo import ASCENDING, IndexModel

from app.models.base import new_uuid, utcnow


class ChatLog(Document):
    id: UUID = Field(default_factory=new_uuid)
    conversation_id: UUID | None = None
    user_id: UUID | None = None
    query: str
    response: str
    citations: list[dict[str, Any]] | None = None
    retrieved_chunk_ids: list[str] | None = None
    latency_ms: int | None = None
    model_used: str | None = None
    created_at: datetime = Field(default_factory=utcnow)

    class Settings:
        name = "chat_logs"
        indexes = [
            IndexModel([("created_at", ASCENDING)]),
            IndexModel([("user_id", ASCENDING)]),
        ]
