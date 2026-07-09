"""Role-based access control."""

from collections.abc import Callable
from typing import Optional

from fastapi import Depends

from app.models.enums import UserRole
from app.models.user import User
from app.utils.exceptions import ForbiddenError

ROLE_PERMISSIONS: dict[UserRole, set[str]] = {
    UserRole.ADMIN: {"*"},
    UserRole.AUTHOR: {
        "chat:read",
        "chat:write",
        "apc:estimate",
        "faqs:read",
        "notifications:read",
    },
    UserRole.REVIEWER: {
        "chat:read",
        "chat:write",
        "apc:estimate",
        "faqs:read",
        "notifications:read",
    },
    UserRole.READER: {
        "chat:read",
        "chat:write",
        "apc:estimate",
        "faqs:read",
        "notifications:read",
    },
}


def has_permission(user: User, permission: str) -> bool:
    perms = ROLE_PERMISSIONS.get(user.role, set())
    return "*" in perms or permission in perms


def require_roles(*roles: UserRole) -> Callable:
    allowed = set(roles)

    def checker(current_user: User = Depends()) -> User:
        if current_user.role not in allowed:
            raise ForbiddenError(f"Requires one of roles: {', '.join(r.value for r in allowed)}")
        return current_user

    return checker


def require_permission(permission: str) -> Callable:
    def checker(current_user: User = Depends()) -> User:
        if not has_permission(current_user, permission):
            raise ForbiddenError(f"Missing permission: {permission}")
        return current_user

    return checker
