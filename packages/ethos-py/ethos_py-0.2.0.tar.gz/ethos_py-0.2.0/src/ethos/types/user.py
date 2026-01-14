"""
User types for Ethos API.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class UserStats(BaseModel):
    """User statistics."""

    class ReviewStats(BaseModel):
        class ReceivedStats(BaseModel):
            positive: int = 0
            neutral: int = 0
            negative: int = 0

        received: ReceivedStats = Field(default_factory=ReceivedStats)

    class VouchStats(BaseModel):
        class GivenStats(BaseModel):
            count: int = 0
            amount_wei_total: int = Field(0, alias="amountWeiTotal")

        class ReceivedStats(BaseModel):
            count: int = 0
            amount_wei_total: int = Field(0, alias="amountWeiTotal")

        given: GivenStats = Field(default_factory=GivenStats)
        received: ReceivedStats = Field(default_factory=ReceivedStats)

    review: ReviewStats = Field(default_factory=ReviewStats)
    vouch: VouchStats = Field(default_factory=VouchStats)

    model_config = {"populate_by_name": True, "extra": "allow"}


class User(BaseModel):
    """
    An Ethos Network user.

    Users are the core entity in Ethos, representing accounts with
    credibility scores and social connections.
    """

    id: int
    profile_id: int | None = Field(None, alias="profileId")
    address: str | None = None

    # Display info
    display_name: str | None = Field(None, alias="displayName")
    username: str | None = None
    avatar_url: str | None = Field(None, alias="avatarUrl")
    description: str | None = None

    # Credibility
    score: int = 0
    status: str = "ACTIVE"

    # Social connections
    userkeys: list[str] = Field(default_factory=list)

    # XP system
    xp_total: int = Field(0, alias="xpTotal")
    xp_streak_days: int = Field(0, alias="xpStreakDays")

    # Influence
    influence_factor: float = Field(0.0, alias="influenceFactor")
    influence_factor_percentile: float = Field(0.0, alias="influenceFactorPercentile")

    # Stats
    stats: UserStats | None = None

    # Timestamps
    created_at: datetime | None = Field(None, alias="createdAt")

    model_config = {"populate_by_name": True, "extra": "allow"}

    @property
    def twitter_handle(self) -> str | None:
        """Extract Twitter handle from userkeys if present."""
        for key in self.userkeys:
            if key.startswith("x.com/user/"):
                return key.replace("x.com/user/", "")
            if key.startswith("twitter.com/user/"):
                return key.replace("twitter.com/user/", "")
        return None

    @property
    def discord_id(self) -> str | None:
        """Extract Discord ID from userkeys if present."""
        for key in self.userkeys:
            if key.startswith("discord.com/user/"):
                return key.replace("discord.com/user/", "")
        return None

    @property
    def farcaster_id(self) -> str | None:
        """Extract Farcaster ID from userkeys if present."""
        for key in self.userkeys:
            if key.startswith("farcaster.xyz/user/fid/"):
                return key.replace("farcaster.xyz/user/fid/", "")
        return None

    @property
    def score_level(self) -> str:
        """Get credibility level based on score."""
        if self.score < 800:
            return "untrusted"
        elif self.score < 1200:
            return "questionable"
        elif self.score < 1600:
            return "neutral"
        elif self.score < 2000:
            return "reputable"
        else:
            return "exemplary"


class CategoryRank(BaseModel):
    """A user's rank in a category."""

    rank: int
    category_id: int = Field(..., alias="categoryId")
    category_name: str | None = Field(None, alias="categoryName")
    category_slug: str | None = Field(None, alias="categorySlug")

    model_config = {"populate_by_name": True, "extra": "allow"}
