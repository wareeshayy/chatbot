"""Admin dashboard service."""

from uuid import UUID

from app.database.repositories.document_repo import DocumentRepository
from app.database.repositories.misc_repo import (
    ChatLogRepository,
    FAQRepository,
    NotificationRepository,
    PolicySettingRepository,
    SuggestedQuestionRepository,
)
from app.models.chat_log import ChatLog
from app.models.conversation import Conversation
from app.models.document import Document
from app.models.enums import DocumentStatus
from app.models.policy import PolicySetting, SuggestedQuestion
from app.models.user import User
from app.schemas.admin import DashboardStatsResponse, PolicySettingUpdateRequest
from app.schemas.chat import SuggestedQuestionCreateRequest
from app.utils.exceptions import NotFoundError
from app.utils.pagination import ServicePage


class AdminService:
    def __init__(self) -> None:
        self.document_repo = DocumentRepository()
        self.faq_repo = FAQRepository()
        self.notification_repo = NotificationRepository()
        self.chat_log_repo = ChatLogRepository()
        self.policy_repo = PolicySettingRepository()
        self.suggested_repo = SuggestedQuestionRepository()

    async def get_dashboard_stats(self) -> DashboardStatsResponse:
        return DashboardStatsResponse(
            total_users=await User.count(),
            total_documents=await Document.find(Document.is_active == True).count(),  # noqa: E712
            indexed_documents=await self.document_repo.count_by_status(DocumentStatus.INDEXED),
            total_conversations=await Conversation.count(),
            total_chat_logs=await ChatLog.count(),
            published_faqs=await self.faq_repo.count_published(),
            active_notifications=await self.notification_repo.count_active_published(),
        )

    async def list_chat_logs(self, page: int = 1, page_size: int = 20) -> ServicePage[ChatLog]:
        offset = (page - 1) * page_size
        logs, total = await self.chat_log_repo.list_logs(offset, page_size)
        return ServicePage.create(logs, total, page, page_size)

    async def get_chat_log(self, log_id: UUID) -> ChatLog:
        log = await self.chat_log_repo.get_by_id(log_id)
        if not log:
            raise NotFoundError("Chat log", log_id)
        return log

    async def list_policies(self) -> list[PolicySetting]:
        return await self.policy_repo.list_all()

    async def update_policy(
        self,
        key: str,
        data: PolicySettingUpdateRequest,
        admin: User,
    ) -> PolicySetting:
        policy = await self.policy_repo.get_by_key(key)
        if not policy:
            policy = PolicySetting(
                key=key,
                value=data.value,
                description=data.description,
                updated_by=admin.id,
            )
            return await self.policy_repo.create(policy)

        policy.value = data.value
        if data.description is not None:
            policy.description = data.description
        policy.updated_by = admin.id
        await policy.save()
        return policy

    async def list_suggested_questions(self) -> list[SuggestedQuestion]:
        return await SuggestedQuestion.find_all().sort(+SuggestedQuestion.display_order).to_list()

    async def create_suggested_question(
        self, data: SuggestedQuestionCreateRequest
    ) -> SuggestedQuestion:
        question = SuggestedQuestion(**data.model_dump())
        return await self.suggested_repo.create(question)

    async def update_suggested_question(
        self, question_id: UUID, data: SuggestedQuestionCreateRequest
    ) -> SuggestedQuestion:
        question = await self.suggested_repo.get_by_id(question_id)
        if not question:
            raise NotFoundError("Suggested question", question_id)

        for field, value in data.model_dump().items():
            setattr(question, field, value)
        await question.save()
        return question

    async def delete_suggested_question(self, question_id: UUID) -> None:
        question = await self.suggested_repo.get_by_id(question_id)
        if not question:
            raise NotFoundError("Suggested question", question_id)
        await self.suggested_repo.delete(question)
