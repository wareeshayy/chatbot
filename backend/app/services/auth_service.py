"""Authentication service."""

from datetime import datetime, timezone

from app.auth.jwt import (
    create_access_token,
    create_refresh_token_value,
    get_refresh_token_expiry,
    hash_refresh_token,
)
from app.auth.password import hash_password, verify_password
from app.config.settings import get_settings
from app.database.repositories.user_repo import RefreshTokenRepository, UserRepository
from app.models.enums import UserRole
from app.models.user import RefreshToken, User
from app.schemas.auth import TokenResponse, UserRegisterRequest
from app.utils.exceptions import ConflictError, UnauthorizedError, ValidationError

settings = get_settings()


class AuthService:
    def __init__(self) -> None:
        self.user_repo = UserRepository()
        self.token_repo = RefreshTokenRepository()

    async def register(self, data: UserRegisterRequest) -> User:
        existing = await self.user_repo.get_by_email(data.email)
        if existing:
            raise ConflictError("Email already registered")

        self._validate_password_strength(data.password)

        user = User(
            email=data.email.lower(),
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            role=UserRole.READER,
        )
        return await self.user_repo.create(user)

    async def login(self, email: str, password: str) -> TokenResponse:
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedError("Account is deactivated")

        user.last_login_at = datetime.now(timezone.utc)
        await user.save()

        return await self._issue_tokens(user)

    async def refresh(self, refresh_token: str) -> TokenResponse:
        token_hash = hash_refresh_token(refresh_token)
        stored = await self.token_repo.get_by_hash(token_hash)

        if not stored or stored.revoked_at is not None:
            raise UnauthorizedError("Invalid refresh token")

        if stored.expires_at < datetime.now(timezone.utc):
            raise UnauthorizedError("Refresh token expired")

        user = await self.user_repo.get_by_id(stored.user_id)
        if not user or not user.is_active:
            raise UnauthorizedError("User not found or inactive")

        stored.revoked_at = datetime.now(timezone.utc)
        await stored.save()
        return await self._issue_tokens(user)

    async def logout(self, refresh_token: str) -> None:
        token_hash = hash_refresh_token(refresh_token)
        stored = await self.token_repo.get_by_hash(token_hash)
        if stored and stored.revoked_at is None:
            stored.revoked_at = datetime.now(timezone.utc)
            await stored.save()

    async def change_password(
        self,
        user: User,
        current_password: str,
        new_password: str,
    ) -> None:
        if not verify_password(current_password, user.hashed_password):
            raise UnauthorizedError("Current password is incorrect")

        self._validate_password_strength(new_password)
        user.hashed_password = hash_password(new_password)
        await user.save()
        await self.token_repo.revoke_all_for_user(user.id)

    async def _issue_tokens(self, user: User) -> TokenResponse:
        access_token = create_access_token(user.id, user.email, user.role)
        refresh_value = create_refresh_token_value()

        refresh_entity = RefreshToken(
            user_id=user.id,
            token_hash=hash_refresh_token(refresh_value),
            expires_at=get_refresh_token_expiry(),
        )
        await self.token_repo.create(refresh_entity)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_value,
            expires_in=settings.access_token_expire_minutes * 60,
        )

    @staticmethod
    def _validate_password_strength(password: str) -> None:
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters")
        if not any(c.isupper() for c in password):
            raise ValidationError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in password):
            raise ValidationError("Password must contain at least one digit")
