"""Suggested questions and policy settings documents."""

from datetime import datetime
from typing import Any
from uuid import UUID

from beanie import Document
from pydantic import Field
from pymongo import ASCENDING, IndexModel

from app.models.base import new_uuid, utcnow
from app.models.enums import UserRole


class SuggestedQuestion(Document):
    id: UUID = Field(default_factory=new_uuid)
    question: str
    category: str | None = None
    target_role: UserRole | None = None
    display_order: int = 0
    is_active: bool = True

    class Settings:
        name = "suggested_questions"
        indexes = [IndexModel([("display_order", ASCENDING)])]


class PolicySetting(Document):
    id: UUID = Field(default_factory=new_uuid)
    key: str
    value: dict[str, Any]
    description: str | None = None
    updated_by: UUID | None = None
    updated_at: datetime = Field(default_factory=utcnow)

    class Settings:
        name = "policy_settings"
        indexes = [IndexModel([("key", ASCENDING)], unique=True)]
