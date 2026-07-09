"""User and refresh token documents."""

from datetime import datetime
from uuid import UUID

from beanie import Document
from pydantic import Field
from pymongo import ASCENDING, IndexModel

from app.models.base import new_uuid, utcnow
from app.models.enums import UserRole


class User(Document):
    id: UUID = Field(default_factory=new_uuid)
    email: str
    hashed_password: str
    full_name: str
    role: UserRole = UserRole.READER
    is_active: bool = True
    is_verified: bool = False
    last_login_at: datetime | None = None
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

    class Settings:
        name = "users"
        indexes = [
            IndexModel([("email", ASCENDING)], unique=True),
            IndexModel([("role", ASCENDING)]),
        ]


class RefreshToken(Document):
    id: UUID = Field(default_factory=new_uuid)
    user_id: UUID
    token_hash: str
    expires_at: datetime
    revoked_at: datetime | None = None
    created_at: datetime = Field(default_factory=utcnow)

    class Settings:
        name = "refresh_tokens"
        indexes = [
            IndexModel([("token_hash", ASCENDING)], unique=True),
            IndexModel([("user_id", ASCENDING)]),
        ]
