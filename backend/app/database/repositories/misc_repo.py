"""APC, FAQ, notification, and admin repositories."""

from datetime import date, datetime, timezone
from uuid import UUID

from app.models.apc_config import APCDiscountRule, APCPricingRule
from app.models.chat_log import ChatLog
from app.models.enums import AuthorCategory, DocumentStatus, PaperType, UserRole
from app.models.faq import FAQ
from app.models.notification import Notification
from app.models.policy import PolicySetting, SuggestedQuestion


class APCPricingRuleRepository:
    async def get_by_id(self, entity_id: UUID) -> APCPricingRule | None:
        return await APCPricingRule.get(entity_id)

    async def create(self, entity: APCPricingRule) -> APCPricingRule:
        await entity.insert()
        return entity

    async def get_active_for_paper_type(
        self,
        paper_type: PaperType,
        on_date: date | None = None,
    ) -> APCPricingRule | None:
        ref_date = on_date or date.today()
        rules = await APCPricingRule.find(
            APCPricingRule.paper_type == paper_type,
            APCPricingRule.is_active == True,  # noqa: E712
            APCPricingRule.effective_from <= ref_date,
        ).to_list()
        for rule in rules:
            if rule.effective_to is None or rule.effective_to >= ref_date:
                return rule
        return None

    async def list_active(self) -> list[APCPricingRule]:
        return await APCPricingRule.find(APCPricingRule.is_active == True).to_list()  # noqa: E712


class APCDiscountRuleRepository:
    async def get_by_id(self, entity_id: UUID) -> APCDiscountRule | None:
        return await APCDiscountRule.get(entity_id)

    async def create(self, entity: APCDiscountRule) -> APCDiscountRule:
        await entity.insert()
        return entity

    async def get_active_for_category(
        self,
        author_category: AuthorCategory,
        on_date: date | None = None,
    ) -> APCDiscountRule | None:
        ref_date = on_date or date.today()
        rules = await APCDiscountRule.find(
            APCDiscountRule.author_category == author_category,
            APCDiscountRule.is_active == True,  # noqa: E712
            APCDiscountRule.effective_from <= ref_date,
        ).to_list()
        for rule in rules:
            if rule.effective_to is None or rule.effective_to >= ref_date:
                return rule
        return None

    async def list_active(self) -> list[APCDiscountRule]:
        return await APCDiscountRule.find(APCDiscountRule.is_active == True).to_list()  # noqa: E712


class FAQRepository:
    async def get_by_id(self, entity_id: UUID) -> FAQ | None:
        return await FAQ.get(entity_id)

    async def create(self, entity: FAQ) -> FAQ:
        await entity.insert()
        return entity

    async def delete(self, entity: FAQ) -> None:
        await entity.delete()

    async def list_faqs(
        self,
        offset: int = 0,
        limit: int = 50,
        category: str | None = None,
        published_only: bool = True,
    ) -> tuple[list[FAQ], int]:
        filters = []
        if published_only:
            filters.append(FAQ.is_published == True)  # noqa: E712
        if category:
            filters.append(FAQ.category == category)
        query = FAQ.find(*filters) if filters else FAQ.find_all()
        total = await query.count()
        faqs = await query.sort(+FAQ.display_order, -FAQ.created_at).skip(offset).limit(limit).to_list()
        return faqs, total

    async def count_published(self) -> int:
        return await FAQ.find(FAQ.is_published == True).count()  # noqa: E712


class NotificationRepository:
    async def get_by_id(self, entity_id: UUID) -> Notification | None:
        return await Notification.get(entity_id)

    async def create(self, entity: Notification) -> Notification:
        await entity.insert()
        return entity

    async def delete(self, entity: Notification) -> None:
        await entity.delete()

    async def list_published(
        self,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Notification], int]:
        query = Notification.find(Notification.is_published == True)  # noqa: E712
        total = await query.count()
        items = await query.sort(-Notification.published_at).skip(offset).limit(limit).to_list()
        return items, total

    async def count_active_published(self) -> int:
        now = datetime.now(timezone.utc)
        notifications = await Notification.find(Notification.is_published == True).to_list()  # noqa: E712
        return sum(1 for n in notifications if n.expires_at is None or n.expires_at > now)


class ChatLogRepository:
    async def get_by_id(self, entity_id: UUID) -> ChatLog | None:
        return await ChatLog.get(entity_id)

    async def create(self, entity: ChatLog) -> ChatLog:
        await entity.insert()
        return entity

    async def list_logs(
        self,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[ChatLog], int]:
        total = await ChatLog.count()
        logs = await ChatLog.find_all().sort(-ChatLog.created_at).skip(offset).limit(limit).to_list()
        return logs, total


class SuggestedQuestionRepository:
    async def get_by_id(self, entity_id: UUID) -> SuggestedQuestion | None:
        return await SuggestedQuestion.get(entity_id)

    async def create(self, entity: SuggestedQuestion) -> SuggestedQuestion:
        await entity.insert()
        return entity

    async def delete(self, entity: SuggestedQuestion) -> None:
        await entity.delete()

    async def list_active(self, role: UserRole | None = None) -> list[SuggestedQuestion]:
        questions = await SuggestedQuestion.find(
            SuggestedQuestion.is_active == True  # noqa: E712
        ).sort(+SuggestedQuestion.display_order).to_list()
        if role:
            questions = [q for q in questions if q.target_role is None or q.target_role == role]
        return questions


class PolicySettingRepository:
    async def create(self, entity: PolicySetting) -> PolicySetting:
        await entity.insert()
        return entity

    async def get_by_key(self, key: str) -> PolicySetting | None:
        return await PolicySetting.find_one(PolicySetting.key == key)

    async def list_all(self) -> list[PolicySetting]:
        return await PolicySetting.find_all().sort(+PolicySetting.key).to_list()
