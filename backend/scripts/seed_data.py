"""Seed MongoDB with IJAIKE APC rules, admin, FAQs, and suggested questions."""

import asyncio
from datetime import date
from decimal import Decimal

from app.auth.password import hash_password
from app.database.mongodb import close_mongo_connection, connect_to_mongo
from app.models.apc_config import APCDiscountRule, APCPricingRule
from app.models.enums import AuthorCategory, DiscountType, PaperType, UserRole
from app.models.faq import FAQ
from app.models.policy import SuggestedQuestion
from app.models.user import User
from app.prompts.system_prompts import DEFAULT_SUGGESTED_QUESTIONS, MANUSCRIPT_CENTRAL_URL


async def seed() -> None:
    await connect_to_mongo()

    if not await User.find_one(User.email == "admin@ijaike.org"):
        await User(
            email="admin@ijaike.org",
            hashed_password=hash_password("Admin@12345"),
            full_name="IJAIKE Administrator",
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True,
        ).insert()
        print("Created admin: admin@ijaike.org / Admin@12345")

    if await APCPricingRule.count() == 0:
        rules = [
            (PaperType.STANDARD_ARTICLE, Decimal("1000"), 20, 20),
            (PaperType.SHORT_PAPER, Decimal("750"), 1, 15),
            (PaperType.REVIEW_ARTICLE, Decimal("1500"), 30, 30),
            (PaperType.LONG_PAPER, Decimal("2000"), 40, 40),
            (PaperType.RESEARCH_ARTICLE, None, 1, None),  # per-page below
        ]
        for paper_type, flat_fee, min_p, max_p in rules:
            await APCPricingRule(
                paper_type=paper_type,
                base_rate_per_page=Decimal("49.00"),
                flat_fee=flat_fee,
                minimum_pages=min_p,
                maximum_pages=max_p,
                effective_from=date.today(),
                is_active=True,
            ).insert()
        print("Seeded IJAIKE APC pricing rules ($49/page + package rates)")

    if await APCDiscountRule.count() == 0:
        discounts = [
            (AuthorCategory.REGULAR, DiscountType.PERCENTAGE, Decimal("0"), False, None),
            (AuthorCategory.SPECIAL_ISSUE_EARLY, DiscountType.PERCENTAGE, Decimal("50"), False,
             "50% discount for early submissions to special issues"),
            (AuthorCategory.PHD_CANDIDATE, DiscountType.PERCENTAGE, Decimal("50"), True,
             "50% waiver for Ph.D. candidates without research grants"),
            (AuthorCategory.INSTITUTIONAL_PARTNER, DiscountType.PERCENTAGE, Decimal("30"), False,
             "Institutional partner discount"),
            (AuthorCategory.STUDENT, DiscountType.PERCENTAGE, Decimal("25"), False, None),
        ]
        for cat, dtype, val, waiver, desc in discounts:
            await APCDiscountRule(
                author_category=cat,
                discount_type=dtype,
                discount_value=val,
                requires_approval=waiver,
                description=desc,
                effective_from=date.today(),
                is_active=True,
            ).insert()
        print("Seeded APC discount rules")

    if await FAQ.count() == 0:
        faqs = [
            (
                "Where do I submit my manuscript?",
                f"You can submit through Manuscript Central: {MANUSCRIPT_CENTRAL_URL}",
                "submission",
            ),
            (
                "What are the APC charges?",
                "JAIKE charges $49/page for accepted manuscripts. Package rates: Standard 20-page ($1,000), "
                "Short 15-page ($750), Review 30-page ($1,500), Long 40-page ($2,000). "
                "No fees for initial submission or peer review.",
                "apc",
            ),
            (
                "What formatting is required?",
                "Letter-size, 1-inch margins, double-spaced, Times New Roman 11pt, Microsoft Word. "
                "Up to 25 pages (6,000–8,000 words). APA 7th edition references.",
                "formatting",
            ),
            (
                "Are APC discounts available?",
                "Yes: 50% for early special issue submissions, 50% waiver for Ph.D. candidates without funding, "
                "and institutional partner discounts.",
                "apc",
            ),
        ]
        for q, a, cat in faqs:
            await FAQ(question=q, answer=a, category=cat, is_published=True).insert()
        print("Seeded FAQs")

    if await SuggestedQuestion.count() == 0:
        for sq in DEFAULT_SUGGESTED_QUESTIONS:
            await SuggestedQuestion(**sq, is_active=True).insert()
        print("Seeded suggested questions")

    await close_mongo_connection()
    print("Seed complete.")


if __name__ == "__main__":
    asyncio.run(seed())
