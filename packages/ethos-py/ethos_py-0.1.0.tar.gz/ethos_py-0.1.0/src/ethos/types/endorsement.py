"""
Endorsement types for Ethos API.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class EndorserProfile(BaseModel):
    """Profile of an endorser."""

    id: int
    display_name: str | None = Field(None, alias="displayName")
    username: str | None = None
    avatar_url: str | None = Field(None, alias="avatarUrl")
    score: int = 0
    stats: dict | None = None

    model_config = {"populate_by_name": True, "extra": "allow"}


class Endorsement(BaseModel):
    """
    An endorsement on Ethos Network.

    Endorsements represent trust relationships between users,
    showing who endorses whom through vouches, reviews, etc.
    """

    activity_id: int = Field(..., alias="activityId")
    endorser_profile_id: int = Field(..., alias="endorserProfileId")
    endorsement_type: str = Field(..., alias="endorsementType")
    source_id: int | None = Field(None, alias="sourceId")
    connection_degree: str | None = Field(None, alias="connectionDegree")
    created_at: datetime | None = Field(None, alias="createdAt")

    # Nested endorser profile
    endorser: EndorserProfile | None = None

    model_config = {"populate_by_name": True, "extra": "allow"}

    @property
    def is_first_degree(self) -> bool:
        """Check if this is a first-degree connection."""
        return self.connection_degree == "1st"

    @property
    def is_vouch(self) -> bool:
        """Check if endorsement is from a vouch."""
        return self.endorsement_type == "vouch"

    @property
    def is_review(self) -> bool:
        """Check if endorsement is from a review."""
        return self.endorsement_type == "review"


class EndorsementSummary(BaseModel):
    """Summary statistics for endorsements."""

    total: int = 0
    mutual_vouches: int = Field(0, alias="mutualVouches")
    you_vouched: int = Field(0, alias="youVouched")
    vouched_for_you: int = Field(0, alias="vouchedForYou")
    positive_reviews: int = Field(0, alias="positiveReviews")
    you_reviewed: int = Field(0, alias="youReviewed")
    reviewed_you: int = Field(0, alias="reviewedYou")

    model_config = {"populate_by_name": True, "extra": "allow"}
