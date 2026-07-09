"""User management API routes (admin)."""

import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query

from app.dependencies import get_current_admin
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.common import MessageResponse, PaginatedResult, PaginationMeta
from app.schemas.user import UserListResponse, UserUpdateRequest
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=PaginatedResult[UserListResponse])
async def list_users(admin: Annotated[User, Depends(get_current_admin)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    role: Optional[UserRole] = None) -> PaginatedResult[UserListResponse]:
    service = UserService()
    result = await service.list_users(page, page_size, role)
    return PaginatedResult(
        items=[UserListResponse.model_validate(u) for u in result.items],
        meta=PaginationMeta(
            total=result.total,
            page=result.page,
            page_size=result.page_size,
            total_pages=result.total_pages))


@router.get("/{user_id}", response_model=UserListResponse)
async def get_user(
    user_id: uuid.UUID, admin: Annotated[User, Depends(get_current_admin)]) -> UserListResponse:
    service = UserService()
    user = await service.get_user(user_id)
    return UserListResponse.model_validate(user)


@router.patch("/{user_id}", response_model=UserListResponse)
async def update_user(
    user_id: uuid.UUID,
    data: UserUpdateRequest, admin: Annotated[User, Depends(get_current_admin)]) -> UserListResponse:
    service = UserService()
    user = await service.update_user(user_id, data)
    return UserListResponse.model_validate(user)


@router.delete("/{user_id}", response_model=MessageResponse)
async def deactivate_user(
    user_id: uuid.UUID, admin: Annotated[User, Depends(get_current_admin)]) -> MessageResponse:
    service = UserService()
    await service.deactivate_user(user_id)
    return MessageResponse(message="User deactivated")
