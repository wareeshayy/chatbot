"""APC pricing, discount, and waiver documents."""

from datetime import date, datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from beanie import Document
from pydantic import BeforeValidator, Field
from pymongo import ASCENDING, IndexModel
from bson.decimal128 import Decimal128

from app.models.base import new_uuid, utcnow
from app.models.enums import AuthorCategory, DiscountType, PaperType, WaiverStatus

def validate_decimal128(v):
    if isinstance(v, Decimal128):
        return v.to_decimal()
    if isinstance(v, float):
        return Decimal(str(v))
    if isinstance(v, (int, str)):
        return Decimal(v)
    return v

DecimalField = Annotated[Decimal, BeforeValidator(validate_decimal128)]


class APCPricingRule(Document):
    id: UUID = Field(default_factory=new_uuid)
    paper_type: PaperType
    base_rate_per_page: DecimalField
    minimum_pages: int = 1
    maximum_pages: int | None = None
    flat_fee: DecimalField | None = None
    currency: str = "USD"
    effective_from: date
    effective_to: date | None = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

    class Settings:
        name = "apc_pricing_rules"
        indexes = [IndexModel([("paper_type", ASCENDING), ("is_active", ASCENDING)])]


class APCDiscountRule(Document):
    id: UUID = Field(default_factory=new_uuid)
    author_category: AuthorCategory
    discount_type: DiscountType
    discount_value: DecimalField
    description: str | None = None
    requires_approval: bool = False
    is_active: bool = True
    effective_from: date
    effective_to: date | None = None
    created_at: datetime = Field(default_factory=utcnow)

    class Settings:
        name = "apc_discount_rules"
        indexes = [IndexModel([("author_category", ASCENDING), ("is_active", ASCENDING)])]


class APCWaiverRequest(Document):
    id: UUID = Field(default_factory=new_uuid)
    user_id: UUID
    author_category: AuthorCategory
    justification: str
    status: WaiverStatus = WaiverStatus.PENDING
    reviewed_by: UUID | None = None
    created_at: datetime = Field(default_factory=utcnow)

    class Settings:
        name = "apc_waiver_requests"
