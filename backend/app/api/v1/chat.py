"""Chat API routes."""

import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Body, Depends, Query

from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.chat import (
    ChatResponse,
    ConversationCreateRequest,
    ConversationListItem,
    ConversationResponse,
    ConversationUpdateRequest,
    MessageCreateRequest,
    MessageResponse,
    PublicAskRequest,
    PublicAskResponse,
    SuggestedQuestionResponse)
from app.schemas.common import MessageResponse as MsgResponse
from app.schemas.common import PaginatedResult, PaginationMeta
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/ask", response_model=PublicAskResponse)
async def ask_public(data: PublicAskRequest) -> PublicAskResponse:
    """Public RAG chat — no login required. Primary IJAIKE chatbot endpoint."""
    service = ChatService()
    history = [{"role": h.role.value, "content": h.content} for h in data.history]
    result = await service.ask_public(data.content, history)
    return PublicAskResponse(
        answer=result.answer,
        citations=result.citations,
        model_used=result.model_used,
        latency_ms=result.latency_ms,
    )


@router.get("/suggested-questions", response_model=list[SuggestedQuestionResponse])
async def get_suggested_questions() -> list[SuggestedQuestionResponse]:
    service = ChatService()
    questions = await service.get_suggested_questions()
    return [SuggestedQuestionResponse.model_validate(q) for q in questions]


def _to_conversation_response(conversation) -> ConversationResponse:
    return ConversationResponse(
        id=conversation.id,
        user_id=conversation.user_id,
        title=conversation.title,
        is_archived=conversation.is_archived,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=[MessageResponse.model_validate(m) for m in conversation.messages])


@router.post("/conversations", response_model=ConversationResponse, status_code=201)
async def create_conversation(current_user: Annotated[User, Depends(get_current_user)],
    data: Annotated[Optional[ConversationCreateRequest], Body()] = None) -> ConversationResponse:
    service = ChatService()
    conversation = await service.create_conversation(current_user, data)
    return _to_conversation_response(conversation)


@router.get("/conversations", response_model=PaginatedResult[ConversationListItem])
async def list_conversations(current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    include_archived: bool = False) -> PaginatedResult[ConversationListItem]:
    service = ChatService()
    result = await service.list_conversations(current_user, page, page_size, include_archived)

    items = [
        ConversationListItem(
            id=conv.id,
            title=conv.title,
            is_archived=conv.is_archived,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            message_count=count)
        for conv, count in result.items
    ]

    return PaginatedResult(
        items=items,
        meta=PaginationMeta(
            total=result.total,
            page=result.page,
            page_size=result.page_size,
            total_pages=result.total_pages))


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: uuid.UUID, current_user: Annotated[User, Depends(get_current_user)]) -> ConversationResponse:
    service = ChatService()
    conversation = await service.get_conversation(current_user, conversation_id)
    return _to_conversation_response(conversation)


@router.patch("/conversations/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: uuid.UUID,
    data: ConversationUpdateRequest, current_user: Annotated[User, Depends(get_current_user)]) -> ConversationResponse:
    service = ChatService()
    conversation = await service.update_conversation(current_user, conversation_id, data)
    return _to_conversation_response(
        await service.get_conversation(current_user, conversation.id)
    )


@router.delete("/conversations/{conversation_id}", response_model=MsgResponse)
async def delete_conversation(
    conversation_id: uuid.UUID, current_user: Annotated[User, Depends(get_current_user)]) -> MsgResponse:
    service = ChatService()
    await service.delete_conversation(current_user, conversation_id)
    return MsgResponse(message="Conversation deleted")


@router.post("/conversations/{conversation_id}/messages", response_model=ChatResponse)
async def send_message(
    conversation_id: uuid.UUID,
    data: MessageCreateRequest, current_user: Annotated[User, Depends(get_current_user)]) -> ChatResponse:
    service = ChatService()
    result = await service.send_message(current_user, conversation_id, data)
    return ChatResponse(
        user_message=MessageResponse.model_validate(result.user_message),
        assistant_message=MessageResponse.model_validate(result.assistant_message))


# suggested-questions moved above /ask
