"""APC estimator schemas."""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import Field

from app.models.enums import AuthorCategory, DiscountType, PaperType
from app.schemas.common import BaseSchema


class APCEstimateRequest(BaseSchema):
    paper_type: PaperType
    num_pages: int = Field(ge=1, le=500)
    author_category: AuthorCategory = AuthorCategory.REGULAR


class APCEstimateResponse(BaseSchema):
    paper_type: PaperType
    num_pages: int
    author_category: AuthorCategory
    base_rate_per_page: Optional[Decimal] = None
    subtotal: Decimal
    discount_type: Optional[DiscountType] = None
    discount_value: Optional[Decimal] = None
    discount_amount: Decimal
    total: Decimal
    currency: str = "USD"
    requires_waiver_approval: bool = False
    breakdown: str


class APCPricingRuleCreate(BaseSchema):
    paper_type: PaperType
    base_rate_per_page: Decimal = Field(ge=0)
    minimum_pages: int = Field(default=1, ge=1)
    maximum_pages: Optional[int] = Field(default=None, ge=1)
    flat_fee: Optional[Decimal] = Field(default=None, ge=0)
    currency: str = "USD"
    effective_from: date
    effective_to: Optional[date] = None
    is_active: bool = True


class APCPricingRuleUpdate(BaseSchema):
    base_rate_per_page: Optional[Decimal] = Field(default=None, ge=0)
    minimum_pages: Optional[int] = Field(default=None, ge=1)
    maximum_pages: Optional[int] = None
    flat_fee: Optional[Decimal] = None
    currency: Optional[str] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    is_active: Optional[bool] = None


class APCPricingRuleResponse(BaseSchema):
    id: UUID
    paper_type: PaperType
    base_rate_per_page: Decimal
    minimum_pages: int
    maximum_pages: Optional[int] = None
    flat_fee: Optional[Decimal] = None
    currency: str
    effective_from: date
    effective_to: Optional[date] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class APCDiscountRuleCreate(BaseSchema):
    author_category: AuthorCategory
    discount_type: DiscountType
    discount_value: Decimal = Field(ge=0)
    description: Optional[str] = None
    requires_approval: bool = False
    effective_from: date
    effective_to: Optional[date] = None
    is_active: bool = True


class APCDiscountRuleUpdate(BaseSchema):
    discount_type: Optional[DiscountType] = None
    discount_value: Optional[Decimal] = Field(default=None, ge=0)
    description: Optional[str] = None
    requires_approval: Optional[bool] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    is_active: Optional[bool] = None


class APCDiscountRuleResponse(BaseSchema):
    id: UUID
    author_category: AuthorCategory
    discount_type: DiscountType
    discount_value: Decimal
    description: Optional[str] = None
    requires_approval: bool
    is_active: bool
    effective_from: date
    effective_to: Optional[date] = None
    created_at: datetime
