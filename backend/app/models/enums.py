"""Shared enumerations used across models and schemas."""

import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    AUTHOR = "author"
    REVIEWER = "reviewer"
    READER = "reader"


class DocumentCategory(str, enum.Enum):
    AUTHOR_GUIDELINES = "author_guidelines"
    APC_POLICY = "apc_policy"
    EDITORIAL_POLICIES = "editorial_policies"
    FAQ = "faq"
    PUBLISHED_PAPER = "published_paper"
    SPECIAL_ISSUE = "special_issue"
    JOURNAL_ANNOUNCEMENT = "journal_announcement"
    CALL_FOR_PAPERS = "call_for_papers"
    OTHER = "other"


class DocumentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"


class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class NotificationType(str, enum.Enum):
    CALL_FOR_PAPERS = "call_for_papers"
    SPECIAL_ISSUE = "special_issue"
    JOURNAL_ANNOUNCEMENT = "journal_announcement"
    GENERAL = "general"


class PaperType(str, enum.Enum):
    STANDARD_ARTICLE = "standard_article"       # 20 pages — $1000
    SHORT_PAPER = "short_paper"                 # 15 pages — $750
    REVIEW_ARTICLE = "review_article"           # 30 pages — $1500
    LONG_PAPER = "long_paper"                   # 40 pages — $2000
    SPECIAL_ISSUE_PAPER = "special_issue_paper" # $800
    RESEARCH_ARTICLE = "research_article"       # per-page $49


class AuthorCategory(str, enum.Enum):
    REGULAR = "regular"
    SPECIAL_ISSUE_EARLY = "special_issue_early"   # 50% discount
    PHD_CANDIDATE = "phd_candidate"             # 50% waiver
    INSTITUTIONAL_PARTNER = "institutional_partner"
    DEVELOPING_COUNTRY = "developing_country"
    STUDENT = "student"
    IJAIKE_MEMBER = "ijaike_member"


class DiscountType(str, enum.Enum):
    PERCENTAGE = "percentage"
    FIXED = "fixed"


class WaiverStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
