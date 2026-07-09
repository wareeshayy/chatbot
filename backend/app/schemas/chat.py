"""Chat schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field

from app.models.enums import MessageRole, UserRole
from app.schemas.common import BaseSchema, CitationSchema


class ConversationCreateRequest(BaseSchema):
    title: Optional[str] = Field(default=None, max_length=500)


class ConversationUpdateRequest(BaseSchema):
    title: Optional[str] = Field(default=None, max_length=500)
    is_archived: Optional[bool] = None


class MessageCreateRequest(BaseSchema):
    content: str = Field(min_length=1, max_length=1000000)


class MessageResponse(BaseSchema):
    id: UUID
    conversation_id: UUID
    role: MessageRole
    content: str
    citations: Optional[list[CitationSchema]] = None
    token_count: Optional[int] = None
    created_at: datetime


class ConversationResponse(BaseSchema):
    id: UUID
    user_id: Optional[UUID] = None
    title: Optional[str] = None
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse] = []


class ConversationListItem(BaseSchema):
    id: UUID
    title: Optional[str] = None
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    message_count: int = 0


class ChatResponse(BaseSchema):
    user_message: MessageResponse
    assistant_message: MessageResponse


class SuggestedQuestionResponse(BaseSchema):
    id: UUID
    question: str
    category: Optional[str] = None
    target_role: Optional[UserRole] = None
    display_order: int


class SuggestedQuestionCreateRequest(BaseSchema):
    question: str = Field(min_length=5, max_length=500)
    category: Optional[str] = None
    target_role: Optional[UserRole] = None
    display_order: int = 0
    is_active: bool = True


class ChatHistoryItem(BaseSchema):
    role: MessageRole
    content: str


class PublicAskRequest(BaseSchema):
    content: str = Field(min_length=1, max_length=1000000)
    history: list[ChatHistoryItem] = Field(default_factory=list)


class PublicAskResponse(BaseSchema):
    answer: str
    citations: list[CitationSchema] = Field(default_factory=list)
    model_used: Optional[str] = None
    latency_ms: int = 0
