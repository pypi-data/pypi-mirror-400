"""
Vote types for Ethos API.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

VoteTargetType = Literal[
    "attestation",
    "bond",
    "broker",
    "discussion",
    "review",
    "slash",
    "vouch",
    "project",
    "reputationMarket",
]


class VoterProfile(BaseModel):
    """Profile of a voter."""

    id: int
    display_name: str | None = Field(None, alias="displayName")
    username: str | None = None
    avatar_url: str | None = Field(None, alias="avatarUrl")
    score: int = 0

    model_config = {"populate_by_name": True, "extra": "allow"}


class Vote(BaseModel):
    """
    A vote on Ethos Network.

    Votes are upvotes or downvotes on various activities like reviews,
    vouches, attestations, etc.
    """

    id: int | None = None
    voter_profile_id: int = Field(..., alias="voterProfileId")
    target_type: str = Field(..., alias="targetType")
    target_id: int = Field(..., alias="targetId")
    is_upvote: bool = Field(..., alias="isUpvote")
    weight: float = 1.0

    # Voter profile
    voter: VoterProfile | None = None
    user: VoterProfile | None = None

    # Timestamps
    created_at: datetime | None = Field(None, alias="createdAt")
    updated_at: datetime | None = Field(None, alias="updatedAt")

    model_config = {"populate_by_name": True, "extra": "allow"}

    @property
    def is_downvote(self) -> bool:
        """Check if this is a downvote."""
        return not self.is_upvote


class VoteStats(BaseModel):
    """Statistics for votes on an activity."""

    upvotes: int = 0
    downvotes: int = 0
    weighted_upvotes: float = Field(0.0, alias="weightedUpvotes")
    weighted_downvotes: float = Field(0.0, alias="weightedDownvotes")
    upvote_percentage: float = Field(0.0, alias="upvotePercentage")
    downvote_percentage: float = Field(0.0, alias="downvotePercentage")

    # User's own vote if authenticated
    user_vote: Vote | None = Field(None, alias="userVote")

    model_config = {"populate_by_name": True, "extra": "allow"}

    @property
    def total_votes(self) -> int:
        """Get total number of votes."""
        return self.upvotes + self.downvotes

    @property
    def net_votes(self) -> int:
        """Get net votes (upvotes - downvotes)."""
        return self.upvotes - self.downvotes
