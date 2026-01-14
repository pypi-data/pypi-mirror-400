"""
Review model for Ethos reviews.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

ReviewScore = Literal["positive", "neutral", "negative"]


class Review(BaseModel):
    """
    A review on Ethos Network.

    Reviews are public ratings that users leave for other users,
    contributing to their credibility score.
    """

    id: int

    # Relationship
    author_profile_id: int = Field(..., alias="authorProfileId")
    target_profile_id: int = Field(..., alias="subjectProfileId")

    # Review content
    score: ReviewScore
    comment: str | None = None

    # Metadata
    archived: bool = False

    # Timestamps
    created_at: datetime | None = Field(None, alias="createdAt")
    updated_at: datetime | None = Field(None, alias="updatedAt")

    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }

    @property
    def is_positive(self) -> bool:
        """Check if this is a positive review."""
        return self.score == "positive"

    @property
    def is_negative(self) -> bool:
        """Check if this is a negative review."""
        return self.score == "negative"

    @property
    def is_neutral(self) -> bool:
        """Check if this is a neutral review."""
        return self.score == "neutral"

    @property
    def reviewer_id(self) -> int:
        """Alias for author_profile_id."""
        return self.author_profile_id

    @property
    def target_id(self) -> int:
        """Alias for target_profile_id."""
        return self.target_profile_id
