"""Shared document helpers for Beanie models."""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_uuid() -> UUID:
    return uuid4()


def uuid_field() -> Field:
    return Field(default_factory=new_uuid)
