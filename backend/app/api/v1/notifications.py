"""Notification API routes."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.dependencies import get_current_admin
from app.models.user import User
from app.schemas.common import MessageResponse, PaginatedResult, PaginationMeta
from app.schemas.notification import (
    NotificationCreateRequest,
    NotificationResponse,
    NotificationUpdateRequest)
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=PaginatedResult[NotificationResponse])
async def list_notifications(page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)) -> PaginatedResult[NotificationResponse]:
    service = NotificationService()
    result = await service.list_published(page, page_size)
    return PaginatedResult(
        items=[NotificationResponse.model_validate(n) for n in result.items],
        meta=PaginationMeta(
            total=result.total,
            page=result.page,
            page_size=result.page_size,
            total_pages=result.total_pages))


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: uuid.UUID) -> NotificationResponse:
    service = NotificationService()
    notification = await service.get_notification(notification_id)
    return NotificationResponse.model_validate(notification)


@router.post("", response_model=NotificationResponse, status_code=201)
async def create_notification(
    data: NotificationCreateRequest, admin: Annotated[User, Depends(get_current_admin)]) -> NotificationResponse:
    service = NotificationService()
    notification = await service.create_notification(data, admin)
    return NotificationResponse.model_validate(notification)


@router.put("/{notification_id}", response_model=NotificationResponse)
async def update_notification(
    notification_id: uuid.UUID,
    data: NotificationUpdateRequest, admin: Annotated[User, Depends(get_current_admin)]) -> NotificationResponse:
    service = NotificationService()
    notification = await service.update_notification(notification_id, data)
    return NotificationResponse.model_validate(notification)


@router.post("/{notification_id}/publish", response_model=NotificationResponse)
async def publish_notification(
    notification_id: uuid.UUID, admin: Annotated[User, Depends(get_current_admin)]) -> NotificationResponse:
    service = NotificationService()
    notification = await service.publish(notification_id)
    return NotificationResponse.model_validate(notification)


@router.delete("/{notification_id}", response_model=MessageResponse)
async def delete_notification(
    notification_id: uuid.UUID, admin: Annotated[User, Depends(get_current_admin)]) -> MessageResponse:
    service = NotificationService()
    await service.delete_notification(notification_id)
    return MessageResponse(message="Notification deleted")
