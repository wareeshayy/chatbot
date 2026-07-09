"""Conversation and message repositories."""

from uuid import UUID

from app.models.conversation import Conversation
from app.models.message import Message


class ConversationRepository:
    async def get_by_id(self, entity_id: UUID) -> Conversation | None:
        return await Conversation.get(entity_id)

    async def create(self, entity: Conversation) -> Conversation:
        await entity.insert()
        return entity

    async def delete(self, entity: Conversation) -> None:
        await Message.find(Message.conversation_id == entity.id).delete()
        await entity.delete()

    async def get_with_messages(self, conversation_id: UUID) -> Conversation | None:
        conversation = await Conversation.get(conversation_id)
        if not conversation:
            return None
        messages = (
            await Message.find(Message.conversation_id == conversation_id)
            .sort(+Message.created_at)
            .to_list()
        )
        conversation.messages = messages
        return conversation

    async def list_by_user(
        self,
        user_id: UUID,
        offset: int = 0,
        limit: int = 20,
        include_archived: bool = False,
    ) -> tuple[list[tuple[Conversation, int]], int]:
        query = Conversation.find(Conversation.user_id == user_id)
        if not include_archived:
            query = Conversation.find(
                Conversation.user_id == user_id,
                Conversation.is_archived == False,  # noqa: E712
            )
        total = await query.count()
        conversations = await query.sort(-Conversation.updated_at).skip(offset).limit(limit).to_list()

        items: list[tuple[Conversation, int]] = []
        for conv in conversations:
            count = await Message.find(Message.conversation_id == conv.id).count()
            items.append((conv, count))
        return items, total


class MessageRepository:
    async def create(self, entity: Message) -> Message:
        await entity.insert()
        return entity

    async def get_recent_by_conversation(
        self,
        conversation_id: UUID,
        limit: int = 12,
    ) -> list[Message]:
        messages = (
            await Message.find(Message.conversation_id == conversation_id)
            .sort(-Message.created_at)
            .limit(limit)
            .to_list()
        )
        messages.reverse()
        return messages
