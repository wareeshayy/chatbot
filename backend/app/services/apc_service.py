"""APC estimation service."""

from decimal import Decimal
from uuid import UUID

from app.database.repositories.misc_repo import APCDiscountRuleRepository, APCPricingRuleRepository
from app.models.apc_config import APCDiscountRule, APCPricingRule
from app.models.enums import AuthorCategory, DiscountType, PaperType
from app.schemas.apc import (
    APCDiscountRuleCreate,
    APCDiscountRuleUpdate,
    APCEstimateRequest,
    APCEstimateResponse,
    APCPricingRuleCreate,
    APCPricingRuleUpdate,
)
from app.utils.exceptions import NotFoundError


class APCService:
    def __init__(self) -> None:
        self.pricing_repo = APCPricingRuleRepository()
        self.discount_repo = APCDiscountRuleRepository()

    async def estimate(self, request: APCEstimateRequest) -> APCEstimateResponse:
        pricing = await self.pricing_repo.get_active_for_paper_type(request.paper_type)
        if not pricing:
            raise NotFoundError("APC pricing rule", request.paper_type.value)

        discount = await self.discount_repo.get_active_for_category(request.author_category)

        pages = request.num_pages
        if pricing.minimum_pages and pages < pricing.minimum_pages:
            pages = pricing.minimum_pages
        if pricing.maximum_pages and pages > pricing.maximum_pages:
            pages = pricing.maximum_pages

        if pricing.flat_fee is not None:
            subtotal = pricing.flat_fee
            breakdown = f"Flat fee for {request.paper_type.value}: ${subtotal}"
        else:
            subtotal = Decimal(str(pages)) * pricing.base_rate_per_page
            breakdown = f"{pages} pages × ${pricing.base_rate_per_page}/page = ${subtotal}"

        discount_amount = Decimal("0")
        discount_type = None
        discount_value = None
        requires_waiver = False

        if discount:
            discount_type = discount.discount_type
            discount_value = discount.discount_value
            requires_waiver = discount.requires_approval

            if discount.discount_type == DiscountType.PERCENTAGE:
                discount_amount = (subtotal * discount.discount_value / Decimal("100")).quantize(
                    Decimal("0.01")
                )
                breakdown += (
                    f". {discount.discount_value}% {request.author_category.value} "
                    f"discount = -${discount_amount}"
                )
            else:
                discount_amount = min(discount.discount_value, subtotal)
                breakdown += (
                    f". ${discount.discount_value} fixed discount for "
                    f"{request.author_category.value} = -${discount_amount}"
                )

        total = max(subtotal - discount_amount, Decimal("0"))

        return APCEstimateResponse(
            paper_type=request.paper_type,
            num_pages=pages,
            author_category=request.author_category,
            base_rate_per_page=pricing.base_rate_per_page if pricing.flat_fee is None else None,
            subtotal=subtotal.quantize(Decimal("0.01")),
            discount_type=discount_type,
            discount_value=discount_value,
            discount_amount=discount_amount.quantize(Decimal("0.01")),
            total=total.quantize(Decimal("0.01")),
            currency=pricing.currency,
            requires_waiver_approval=requires_waiver,
            breakdown=breakdown,
        )

    async def list_pricing_rules(self) -> list[APCPricingRule]:
        return await self.pricing_repo.list_active()

    async def create_pricing_rule(self, data: APCPricingRuleCreate) -> APCPricingRule:
        return await self.pricing_repo.create(APCPricingRule(**data.model_dump()))

    async def update_pricing_rule(self, rule_id: UUID, data: APCPricingRuleUpdate) -> APCPricingRule:
        rule = await self.pricing_repo.get_by_id(rule_id)
        if not rule:
            raise NotFoundError("APC pricing rule", rule_id)

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(rule, field, value)
        await rule.save()
        return rule

    async def list_discount_rules(self) -> list[APCDiscountRule]:
        return await self.discount_repo.list_active()

    async def create_discount_rule(self, data: APCDiscountRuleCreate) -> APCDiscountRule:
        return await self.discount_repo.create(APCDiscountRule(**data.model_dump()))

    async def update_discount_rule(self, rule_id: UUID, data: APCDiscountRuleUpdate) -> APCDiscountRule:
        rule = await self.discount_repo.get_by_id(rule_id)
        if not rule:
            raise NotFoundError("APC discount rule", rule_id)

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(rule, field, value)
        await rule.save()
        return rule

    def get_paper_types(self) -> list[dict]:
        return [{"value": pt.value, "label": pt.value.replace("_", " ").title()} for pt in PaperType]

    def get_author_categories(self) -> list[dict]:
        return [
            {"value": ac.value, "label": ac.value.replace("_", " ").title()}
            for ac in AuthorCategory
        ]
