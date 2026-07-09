"""Pagination utilities."""

from dataclasses import dataclass
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


@dataclass
class ServicePage(Generic[T]):
    """Internal service-layer pagination result (not a Pydantic model)."""

    items: list[T]
    total: int
    page: int
    page_size: int

    @property
    def total_pages(self) -> int:
        return max(1, (self.total + self.page_size - 1) // self.page_size) if self.total > 0 else 0

    @classmethod
    def create(cls, items: list[T], total: int, page: int, page_size: int) -> "ServicePage[T]":
        return cls(items=items, total=total, page=page, page_size=page_size)


class PaginatedResponse(BaseModel, Generic[T]):
    """Legacy alias — prefer ServicePage in services, PaginatedResult in API schemas."""

    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def create(
        cls,
        items: list[T],
        total: int,
        page: int,
        page_size: int,
    ) -> "PaginatedResponse[T]":
        total_pages = max(1, (total + page_size - 1) // page_size) if total > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
