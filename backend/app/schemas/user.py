"""User management schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import EmailStr, Field

from app.models.enums import UserRole
from app.schemas.common import BaseSchema


class UserUpdateRequest(BaseSchema):
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=255)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserListResponse(BaseSchema):
    id: UUID
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None
