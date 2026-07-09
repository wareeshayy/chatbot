"""Admin dashboard API routes."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.dependencies import get_current_admin
from app.models.user import User
from app.schemas.admin import (
    ChatLogResponse,
    DashboardStatsResponse,
    PolicySettingResponse,
    PolicySettingUpdateRequest)
from app.schemas.chat import SuggestedQuestionCreateRequest, SuggestedQuestionResponse
from app.schemas.common import MessageResponse, PaginatedResult, PaginationMeta
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard", response_model=DashboardStatsResponse)
async def get_dashboard(admin: Annotated[User, Depends(get_current_admin)]) -> DashboardStatsResponse:
    service = AdminService()
    return await service.get_dashboard_stats()


@router.get("/chat-logs", response_model=PaginatedResult[ChatLogResponse])
async def list_chat_logs(admin: Annotated[User, Depends(get_current_admin)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)) -> PaginatedResult[ChatLogResponse]:
    service = AdminService()
    result = await service.list_chat_logs(page, page_size)
    return PaginatedResult(
        items=[ChatLogResponse.model_validate(log) for log in result.items],
        meta=PaginationMeta(
            total=result.total,
            page=result.page,
            page_size=result.page_size,
            total_pages=result.total_pages))


@router.get("/chat-logs/{log_id}", response_model=ChatLogResponse)
async def get_chat_log(
    log_id: uuid.UUID, admin: Annotated[User, Depends(get_current_admin)]) -> ChatLogResponse:
    service = AdminService()
    log = await service.get_chat_log(log_id)
    return ChatLogResponse.model_validate(log)


@router.get("/policies", response_model=list[PolicySettingResponse])
async def list_policies(admin: Annotated[User, Depends(get_current_admin)]) -> list[PolicySettingResponse]:
    service = AdminService()
    policies = await service.list_policies()
    return [PolicySettingResponse.model_validate(p) for p in policies]


@router.put("/policies/{key}", response_model=PolicySettingResponse)
async def update_policy(
    key: str,
    data: PolicySettingUpdateRequest, admin: Annotated[User, Depends(get_current_admin)]) -> PolicySettingResponse:
    service = AdminService()
    policy = await service.update_policy(key, data, admin)
    return PolicySettingResponse.model_validate(policy)


@router.get("/suggested-questions", response_model=list[SuggestedQuestionResponse])
async def list_suggested_questions(admin: Annotated[User, Depends(get_current_admin)]) -> list[SuggestedQuestionResponse]:
    service = AdminService()
    questions = await service.list_suggested_questions()
    return [SuggestedQuestionResponse.model_validate(q) for q in questions]


@router.post("/suggested-questions", response_model=SuggestedQuestionResponse, status_code=201)
async def create_suggested_question(
    data: SuggestedQuestionCreateRequest, admin: Annotated[User, Depends(get_current_admin)]) -> SuggestedQuestionResponse:
    service = AdminService()
    question = await service.create_suggested_question(data)
    return SuggestedQuestionResponse.model_validate(question)


@router.put("/suggested-questions/{question_id}", response_model=SuggestedQuestionResponse)
async def update_suggested_question(
    question_id: uuid.UUID,
    data: SuggestedQuestionCreateRequest, admin: Annotated[User, Depends(get_current_admin)]) -> SuggestedQuestionResponse:
    service = AdminService()
    question = await service.update_suggested_question(question_id, data)
    return SuggestedQuestionResponse.model_validate(question)


@router.delete("/suggested-questions/{question_id}", response_model=MessageResponse)
async def delete_suggested_question(
    question_id: uuid.UUID, admin: Annotated[User, Depends(get_current_admin)]) -> MessageResponse:
    service = AdminService()
    await service.delete_suggested_question(question_id)
    return MessageResponse(message="Suggested question deleted")
