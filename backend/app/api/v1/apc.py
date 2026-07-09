"""APC estimator API routes."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import get_current_admin
from app.models.user import User
from app.schemas.apc import (
    APCDiscountRuleCreate,
    APCDiscountRuleResponse,
    APCDiscountRuleUpdate,
    APCEstimateRequest,
    APCEstimateResponse,
    APCPricingRuleCreate,
    APCPricingRuleResponse,
    APCPricingRuleUpdate)
from app.services.apc_service import APCService

router = APIRouter(prefix="/apc", tags=["APC Estimator"])


@router.post("/estimate", response_model=APCEstimateResponse)
async def estimate_apc(data: APCEstimateRequest) -> APCEstimateResponse:
    service = APCService()
    return await service.estimate(data)


@router.get("/paper-types")
async def get_paper_types() -> list[dict]:
    service = APCService()
    return service.get_paper_types()


@router.get("/author-categories")
async def get_author_categories() -> list[dict]:
    service = APCService()
    return service.get_author_categories()


@router.get("/pricing-rules", response_model=list[APCPricingRuleResponse])
async def list_pricing_rules(admin: Annotated[User, Depends(get_current_admin)]) -> list[APCPricingRuleResponse]:
    service = APCService()
    rules = await service.list_pricing_rules()
    return [APCPricingRuleResponse.model_validate(r) for r in rules]


@router.post("/pricing-rules", response_model=APCPricingRuleResponse, status_code=201)
async def create_pricing_rule(
    data: APCPricingRuleCreate, admin: Annotated[User, Depends(get_current_admin)]) -> APCPricingRuleResponse:
    service = APCService()
    rule = await service.create_pricing_rule(data)
    return APCPricingRuleResponse.model_validate(rule)


@router.put("/pricing-rules/{rule_id}", response_model=APCPricingRuleResponse)
async def update_pricing_rule(
    rule_id: uuid.UUID,
    data: APCPricingRuleUpdate, admin: Annotated[User, Depends(get_current_admin)]) -> APCPricingRuleResponse:
    service = APCService()
    rule = await service.update_pricing_rule(rule_id, data)
    return APCPricingRuleResponse.model_validate(rule)


@router.get("/discount-rules", response_model=list[APCDiscountRuleResponse])
async def list_discount_rules(admin: Annotated[User, Depends(get_current_admin)]) -> list[APCDiscountRuleResponse]:
    service = APCService()
    rules = await service.list_discount_rules()
    return [APCDiscountRuleResponse.model_validate(r) for r in rules]


@router.post("/discount-rules", response_model=APCDiscountRuleResponse, status_code=201)
async def create_discount_rule(
    data: APCDiscountRuleCreate, admin: Annotated[User, Depends(get_current_admin)]) -> APCDiscountRuleResponse:
    service = APCService()
    rule = await service.create_discount_rule(data)
    return APCDiscountRuleResponse.model_validate(rule)


@router.put("/discount-rules/{rule_id}", response_model=APCDiscountRuleResponse)
async def update_discount_rule(
    rule_id: uuid.UUID,
    data: APCDiscountRuleUpdate, admin: Annotated[User, Depends(get_current_admin)]) -> APCDiscountRuleResponse:
    service = APCService()
    rule = await service.update_discount_rule(rule_id, data)
    return APCDiscountRuleResponse.model_validate(rule)
