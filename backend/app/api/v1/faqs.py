"""FAQ API routes."""

import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query

from app.dependencies import get_current_admin
from app.models.user import User
from app.schemas.common import MessageResponse, PaginatedResult, PaginationMeta
from app.schemas.faq import FAQCreateRequest, FAQResponse, FAQUpdateRequest
from app.services.faq_service import FAQService

router = APIRouter(prefix="/faqs", tags=["FAQs"])


@router.get("", response_model=PaginatedResult[FAQResponse])
async def list_faqs(page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    category: Optional[str] = None) -> PaginatedResult[FAQResponse]:
    service = FAQService()
    result = await service.list_faqs(page, page_size, category, published_only=True)
    return PaginatedResult(
        items=[FAQResponse.model_validate(f) for f in result.items],
        meta=PaginationMeta(
            total=result.total,
            page=result.page,
            page_size=result.page_size,
            total_pages=result.total_pages))


@router.get("/{faq_id}", response_model=FAQResponse)
async def get_faq(faq_id: uuid.UUID) -> FAQResponse:
    service = FAQService()
    faq = await service.get_faq(faq_id, published_only=True)
    return FAQResponse.model_validate(faq)


@router.post("", response_model=FAQResponse, status_code=201)
async def create_faq(
    data: FAQCreateRequest, admin: Annotated[User, Depends(get_current_admin)]) -> FAQResponse:
    service = FAQService()
    faq = await service.create_faq(data, admin)
    return FAQResponse.model_validate(faq)


@router.put("/{faq_id}", response_model=FAQResponse)
async def update_faq(
    faq_id: uuid.UUID,
    data: FAQUpdateRequest, admin: Annotated[User, Depends(get_current_admin)]) -> FAQResponse:
    service = FAQService()
    faq = await service.update_faq(faq_id, data)
    return FAQResponse.model_validate(faq)


@router.delete("/{faq_id}", response_model=MessageResponse)
async def delete_faq(
    faq_id: uuid.UUID, admin: Annotated[User, Depends(get_current_admin)]) -> MessageResponse:
    service = FAQService()
    await service.delete_faq(faq_id)
    return MessageResponse(message="FAQ deleted")
