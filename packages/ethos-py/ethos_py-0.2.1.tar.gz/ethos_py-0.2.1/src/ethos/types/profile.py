"""
Profile model for Ethos users.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ProfileStats(BaseModel):
    """Statistics about a profile's reviews and vouches."""

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


class ProfileLinks(BaseModel):
    """Links associated with a profile."""

    profile: str | None = None
    score_breakdown: str | None = Field(None, alias="scoreBreakdown")


class Profile(BaseModel):
    """
    An Ethos Network profile.

    Represents a user on the Ethos Network with their credibility score,
    linked social accounts, and reputation statistics.
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
    xp_removed_due_to_abuse: bool = Field(False, alias="xpRemovedDueToAbuse")

    # Influence
    influence_factor: float = Field(0.0, alias="influenceFactor")
    influence_factor_percentile: float = Field(0.0, alias="influenceFactorPercentile")

    # Nested objects
    links: ProfileLinks = Field(default_factory=ProfileLinks)
    stats: ProfileStats = Field(default_factory=ProfileStats)

    # Timestamps
    created_at: datetime | None = Field(None, alias="createdAt")

    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }

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
    def ethereum_address(self) -> str | None:
        """Get the primary Ethereum address."""
        return self.address

    @property
    def credibility_score(self) -> int:
        """Alias for score."""
        return self.score

    @property
    def score_level(self) -> str:
        """
        Get the credibility level based on score.

        Score ranges (from Ethos docs):
        - 0-799: Untrusted
        - 800-1199: Questionable
        - 1200-1599: Neutral
        - 1600-1999: Reputable
        - 2000-2800: Exemplary
        """
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

    @property
    def vouches_received_count(self) -> int:
        """Number of vouches received."""
        return self.stats.vouch.received.count

    @property
    def vouches_given_count(self) -> int:
        """Number of vouches given."""
        return self.stats.vouch.given.count

    @property
    def reviews_positive(self) -> int:
        """Number of positive reviews received."""
        return self.stats.review.received.positive

    @property
    def reviews_negative(self) -> int:
        """Number of negative reviews received."""
        return self.stats.review.received.negative
