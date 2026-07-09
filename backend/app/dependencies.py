"""FastAPI dependency injection."""

import uuid
from typing import Annotated, Optional

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.jwt import decode_access_token
from app.auth.permissions import has_permission
from app.database.repositories.user_repo import UserRepository
from app.models.enums import UserRole
from app.models.user import User
from app.utils.exceptions import ForbiddenError, UnauthorizedError

security = HTTPBearer(auto_error=False)


async def get_current_user_optional(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
) -> Optional[User]:
    if not credentials:
        return None

    payload = decode_access_token(credentials.credentials)
    user_id = uuid.UUID(payload["sub"])
    user = await UserRepository().get_by_id(user_id)

    if not user or not user.is_active:
        raise UnauthorizedError("User not found or inactive")
    return user


async def get_current_user(
    user: Annotated[Optional[User], Depends(get_current_user_optional)],
) -> User:
    if not user:
        raise UnauthorizedError("Authentication required")
    return user


async def get_current_admin(
    user: Annotated[User, Depends(get_current_user)],
) -> User:
    if user.role != UserRole.ADMIN:
        raise ForbiddenError("Admin access required")
    return user


def require_permission_dep(permission: str):
    async def checker(user: Annotated[User, Depends(get_current_user)]) -> User:
        if not has_permission(user, permission):
            raise ForbiddenError(f"Missing permission: {permission}")
        return user

    return checker


async def get_request_id(
    x_request_id: Annotated[Optional[str], Header(alias="X-Request-ID")] = None,
) -> str:
    return x_request_id or str(uuid.uuid4())
