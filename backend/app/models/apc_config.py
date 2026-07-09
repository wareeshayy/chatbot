"""APC pricing, discount, and waiver documents."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from beanie import Document
from pydantic import Field
from pymongo import ASCENDING, IndexModel

from app.models.base import new_uuid, utcnow
from app.models.enums import AuthorCategory, DiscountType, PaperType, WaiverStatus


class APCPricingRule(Document):
    id: UUID = Field(default_factory=new_uuid)
    paper_type: PaperType
    base_rate_per_page: Decimal
    minimum_pages: int = 1
    maximum_pages: int | None = None
    flat_fee: Decimal | None = None
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
    discount_value: Decimal
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
