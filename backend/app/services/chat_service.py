"""Chat conversation service."""

import time
from dataclasses import dataclass
from uuid import UUID

from app.database.repositories.conversation_repo import ConversationRepository, MessageRepository
from app.database.repositories.misc_repo import ChatLogRepository, SuggestedQuestionRepository
from app.models.base import utcnow
from app.models.chat_log import ChatLog
from app.models.conversation import Conversation
from app.models.enums import MessageRole, UserRole
from app.models.message import Message
from app.models.policy import SuggestedQuestion
from app.models.user import User
from app.schemas.chat import (
    ChatResponse,
    ConversationCreateRequest,
    ConversationUpdateRequest,
    MessageCreateRequest,
)
from app.services.rag_service import RAGService
from app.utils.exceptions import ForbiddenError, NotFoundError


@dataclass
class ConversationListResult:
    items: list[tuple[Conversation, int]]
    total: int
    page: int
    page_size: int

    @property
    def total_pages(self) -> int:
        return max(1, (self.total + self.page_size - 1) // self.page_size) if self.total > 0 else 0


@dataclass
class PublicAskResult:
    answer: str
    citations: list
    model_used: str | None
    latency_ms: int
    retrieved_chunk_ids: list[str]


class ChatService:
    def __init__(self) -> None:
        self.conversation_repo = ConversationRepository()
        self.message_repo = MessageRepository()
        self.chat_log_repo = ChatLogRepository()
        self.suggested_repo = SuggestedQuestionRepository()
        self.rag_service = RAGService()

    async def create_conversation(
        self,
        user: User,
        data: ConversationCreateRequest | None = None,
    ) -> Conversation:
        conversation = Conversation(
            user_id=user.id,
            title=data.title if data and data.title else "New Conversation",
        )
        return await self.conversation_repo.create(conversation)

    async def list_conversations(
        self,
        user: User,
        page: int = 1,
        page_size: int = 20,
        include_archived: bool = False,
    ) -> ConversationListResult:
        offset = (page - 1) * page_size
        items, total = await self.conversation_repo.list_by_user(
            user.id, offset, page_size, include_archived
        )
        return ConversationListResult(items=items, total=total, page=page, page_size=page_size)

    async def get_conversation(self, user: User, conversation_id: UUID) -> Conversation:
        conversation = await self.conversation_repo.get_with_messages(conversation_id)
        if not conversation:
            raise NotFoundError("Conversation", conversation_id)
        if conversation.user_id != user.id and user.role.value != "admin":
            raise ForbiddenError("You do not have access to this conversation")
        return conversation

    async def update_conversation(
        self,
        user: User,
        conversation_id: UUID,
        data: ConversationUpdateRequest,
    ) -> Conversation:
        conversation = await self.get_conversation(user, conversation_id)

        if data.title is not None:
            conversation.title = data.title
        if data.is_archived is not None:
            conversation.is_archived = data.is_archived

        conversation.updated_at = utcnow()
        await conversation.save()
        return conversation

    async def delete_conversation(self, user: User, conversation_id: UUID) -> None:
        conversation = await self.get_conversation(user, conversation_id)
        await self.conversation_repo.delete(conversation)

    async def send_message(
        self,
        user: User,
        conversation_id: UUID,
        data: MessageCreateRequest,
    ) -> ChatResponse:
        conversation = await self.get_conversation(user, conversation_id)
        start = time.perf_counter()

        if conversation.title == "New Conversation" or not conversation.title:
            conversation.title = data.content[:80] + ("..." if len(data.content) > 80 else "")
            conversation.updated_at = utcnow()
            await conversation.save()

        user_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content=data.content,
        )
        await self.message_repo.create(user_message)

        history = await self.message_repo.get_recent_by_conversation(conversation.id, limit=12)
        history_dicts = [{"role": m.role.value, "content": m.content} for m in history[:-1]]

        rag_result = await self.rag_service.retrieve_and_generate(data.content, history_dicts)
        citations_data = [c.model_dump(mode="json") for c in rag_result.citations]

        assistant_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=rag_result.answer,
            citations=citations_data,
        )
        await self.message_repo.create(assistant_message)

        latency_ms = int((time.perf_counter() - start) * 1000)

        chat_log = ChatLog(
            conversation_id=conversation.id,
            user_id=user.id,
            query=data.content,
            response=rag_result.answer,
            citations=citations_data,
            retrieved_chunk_ids=rag_result.retrieved_chunk_ids,
            latency_ms=latency_ms,
            model_used=rag_result.model_used,
        )
        await self.chat_log_repo.create(chat_log)

        return ChatResponse(user_message=user_message, assistant_message=assistant_message)

    async def ask_public(
        self,
        content: str,
        history: list[dict] | None = None,
    ) -> PublicAskResult:
        start = time.perf_counter()
        history_dicts = [{"role": h["role"], "content": h["content"]} for h in (history or [])]
        rag_result = await self.rag_service.retrieve_and_generate(content, history_dicts)
        latency_ms = int((time.perf_counter() - start) * 1000)

        chat_log = ChatLog(
            query=content,
            response=rag_result.answer,
            citations=[c.model_dump(mode="json") for c in rag_result.citations],
            retrieved_chunk_ids=rag_result.retrieved_chunk_ids,
            latency_ms=latency_ms,
            model_used=rag_result.model_used,
        )
        try:
            await self.chat_log_repo.create(chat_log)
        except Exception:
            pass  # don't block chat on slow/failed MongoDB logging

        return PublicAskResult(
            answer=rag_result.answer,
            citations=rag_result.citations,
            model_used=rag_result.model_used,
            latency_ms=latency_ms,
            retrieved_chunk_ids=rag_result.retrieved_chunk_ids,
        )

    async def get_suggested_questions(
        self,
        role: UserRole | None = None,
    ) -> list[SuggestedQuestion]:
        return await self.suggested_repo.list_active(role)
