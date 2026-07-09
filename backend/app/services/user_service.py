"""User management service."""

from uuid import UUID

from app.database.repositories.user_repo import UserRepository
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.user import UserUpdateRequest
from app.utils.exceptions import NotFoundError
from app.utils.pagination import ServicePage


class UserService:
    def __init__(self) -> None:
        self.user_repo = UserRepository()

    async def get_user(self, user_id: UUID) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User", user_id)
        return user

    async def list_users(
        self,
        page: int = 1,
        page_size: int = 20,
        role: UserRole | None = None,
    ) -> ServicePage[User]:
        offset = (page - 1) * page_size
        users, total = await self.user_repo.list_users(offset, page_size, role)
        return ServicePage.create(users, total, page, page_size)

    async def update_user(self, user_id: UUID, data: UserUpdateRequest) -> User:
        user = await self.get_user(user_id)

        if data.full_name is not None:
            user.full_name = data.full_name
        if data.role is not None:
            user.role = data.role
        if data.is_active is not None:
            user.is_active = data.is_active

        await user.save()
        return user

    async def deactivate_user(self, user_id: UUID) -> User:
        user = await self.get_user(user_id)
        user.is_active = False
        await user.save()
        return user
