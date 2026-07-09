"""Admin dashboard schemas."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from app.schemas.common import BaseSchema, CitationSchema


class DashboardStatsResponse(BaseSchema):
    total_users: int
    total_documents: int
    indexed_documents: int
    total_conversations: int
    total_chat_logs: int
    published_faqs: int
    active_notifications: int


class ChatLogResponse(BaseSchema):
    id: UUID
    conversation_id: UUID
    user_id: Optional[UUID] = None
    query: str
    response: str
    citations: Optional[list[CitationSchema]] = None
    retrieved_chunk_ids: Optional[list[str]] = None
    latency_ms: Optional[int] = None
    model_used: Optional[str] = None
    created_at: datetime


class PolicySettingResponse(BaseSchema):
    id: UUID
    key: str
    value: dict[str, Any]
    description: Optional[str] = None
    updated_by: Optional[UUID] = None
    updated_at: datetime


class PolicySettingUpdateRequest(BaseSchema):
    value: dict[str, Any]
    description: Optional[str] = None
