"""
Pagination models for Ethos API responses.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationInfo(BaseModel):
    """Pagination metadata from API responses."""

    total: int = 0
    limit: int = 20
    offset: int = 0
    has_more: bool = Field(False, alias="hasMore")

    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }

    @property
    def page(self) -> int:
        """Get current page number (1-indexed)."""
        if self.limit == 0:
            return 1
        return (self.offset // self.limit) + 1

    @property
    def total_pages(self) -> int:
        """Get total number of pages."""
        if self.limit == 0:
            return 1
        return (self.total + self.limit - 1) // self.limit


class PaginatedResponse(BaseModel, Generic[T]):
    """
    A paginated response from the Ethos API.

    Contains both the data items and pagination metadata.
    """

    data: list[T] = Field(default_factory=list)
    pagination: PaginationInfo = Field(default_factory=PaginationInfo)

    model_config = {
        "extra": "allow",
    }

    def __iter__(self) -> Iterator[T]:  # type: ignore[override]
        """Iterate over data items."""
        return iter(self.data)

    def __len__(self) -> int:
        """Get number of items in this page."""
        return len(self.data)

    def __getitem__(self, index: int) -> T:
        """Get item by index."""
        return self.data[index]

    @property
    def has_more(self) -> bool:
        """Check if there are more pages."""
        return self.pagination.has_more

    @property
    def total(self) -> int:
        """Get total number of items across all pages."""
        return self.pagination.total

    @property
    def is_empty(self) -> bool:
        """Check if response contains no items."""
        return len(self.data) == 0
