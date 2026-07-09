"""Notification management service."""

from datetime import datetime, timezone
from uuid import UUID

from app.database.repositories.misc_repo import NotificationRepository
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationCreateRequest, NotificationUpdateRequest
from app.utils.exceptions import NotFoundError
from app.utils.pagination import ServicePage


class NotificationService:
    def __init__(self) -> None:
        self.notification_repo = NotificationRepository()

    async def list_published(
        self,
        page: int = 1,
        page_size: int = 20,
    ) -> ServicePage[Notification]:
        offset = (page - 1) * page_size
        items, total = await self.notification_repo.list_published(offset, page_size)
        return ServicePage.create(items, total, page, page_size)

    async def get_notification(self, notification_id: UUID) -> Notification:
        notification = await self.notification_repo.get_by_id(notification_id)
        if not notification:
            raise NotFoundError("Notification", notification_id)
        return notification

    async def create_notification(
        self,
        data: NotificationCreateRequest,
        admin: User,
    ) -> Notification:
        notification = Notification(**data.model_dump(), created_by=admin.id)
        return await self.notification_repo.create(notification)

    async def update_notification(
        self,
        notification_id: UUID,
        data: NotificationUpdateRequest,
    ) -> Notification:
        notification = await self.get_notification(notification_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(notification, field, value)
        await notification.save()
        return notification

    async def publish(self, notification_id: UUID) -> Notification:
        notification = await self.get_notification(notification_id)
        notification.is_published = True
        notification.published_at = datetime.now(timezone.utc)
        await notification.save()
        return notification

    async def delete_notification(self, notification_id: UUID) -> None:
        notification = await self.get_notification(notification_id)
        await self.notification_repo.delete(notification)
