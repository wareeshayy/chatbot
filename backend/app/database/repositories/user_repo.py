"""User repository."""

from datetime import datetime, timezone
from uuid import UUID

from app.models.enums import UserRole
from app.models.user import RefreshToken, User


class UserRepository:
    async def get_by_id(self, entity_id: UUID) -> User | None:
        return await User.get(entity_id)

    async def create(self, entity: User) -> User:
        await entity.insert()
        return entity

    async def get_by_email(self, email: str) -> User | None:
        return await User.find_one(User.email == email.lower())

    async def list_users(
        self,
        offset: int = 0,
        limit: int = 20,
        role: UserRole | None = None,
    ) -> tuple[list[User], int]:
        query = User.find_all()
        if role:
            query = User.find(User.role == role)
        total = await query.count()
        users = await query.sort(-User.created_at).skip(offset).limit(limit).to_list()
        return users, total


class RefreshTokenRepository:
    async def create(self, entity: RefreshToken) -> RefreshToken:
        await entity.insert()
        return entity

    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        return await RefreshToken.find_one(RefreshToken.token_hash == token_hash)

    async def revoke_all_for_user(self, user_id: UUID) -> None:
        tokens = await RefreshToken.find(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at == None,  # noqa: E711
        ).to_list()
        now = datetime.now(timezone.utc)
        for token in tokens:
            token.revoked_at = now
            await token.save()
