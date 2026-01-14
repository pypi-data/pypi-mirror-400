"""
Score model for Ethos credibility scores.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ScoreBreakdown(BaseModel):
    """Breakdown of factors contributing to a credibility score."""

    reviews: float = 0.0
    vouches: float = 0.0
    attestations: float = 0.0
    activity: float = 0.0
    history: float = 0.0

    model_config = {
        "extra": "allow",
    }


class Score(BaseModel):
    """
    A credibility score on Ethos Network.

    Scores represent the overall trustworthiness of a profile,
    calculated from reviews, vouches, attestations, and activity.

    Score ranges:
    - 0-799: Untrusted
    - 800-1199: Questionable
    - 1200-1599: Neutral
    - 1600-1999: Reputable
    - 2000-2800: Exemplary
    """

    profile_id: int = Field(..., alias="profileId")
    address: str | None = None

    # Score value
    value: int = 0

    # Breakdown
    breakdown: ScoreBreakdown = Field(default_factory=ScoreBreakdown)

    # Percentile ranking
    percentile: float | None = None

    # Timestamps
    updated_at: datetime | None = Field(None, alias="updatedAt")

    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }

    @property
    def level(self) -> str:
        """
        Get the credibility level based on score value.
        """
        if self.value < 800:
            return "untrusted"
        elif self.value < 1200:
            return "questionable"
        elif self.value < 1600:
            return "neutral"
        elif self.value < 2000:
            return "reputable"
        else:
            return "exemplary"

    @property
    def is_trusted(self) -> bool:
        """Check if score indicates trusted status (reputable or better)."""
        return self.value >= 1600

    @property
    def is_untrusted(self) -> bool:
        """Check if score indicates untrusted status."""
        return self.value < 800
