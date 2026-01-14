"""
XP (Experience Points) types for Ethos API.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

DecisionType = Literal["SPEND", "DELEGATE", "NOTHING"]


class XPHistoryEntry(BaseModel):
    """An entry in a user's XP history."""

    id: int
    type: str
    points: int
    metadata: dict | None = None
    week: int | None = None
    xp_season_id: int | None = Field(None, alias="xpSeasonId")
    created_at: datetime | None = Field(None, alias="createdAt")

    model_config = {"populate_by_name": True, "extra": "allow"}


class XPWeeklyData(BaseModel):
    """Weekly XP data for a user."""

    week: int
    weekly_xp: int = Field(..., alias="weeklyXp")
    cumulative_xp: int = Field(..., alias="cumulativeXp")

    model_config = {"populate_by_name": True, "extra": "allow"}


class XPSeason(BaseModel):
    """An XP season."""

    id: int
    name: str | None = None
    start_date: datetime | None = Field(None, alias="startDate")
    end_date: datetime | None = Field(None, alias="endDate")
    is_active: bool = Field(False, alias="isActive")

    model_config = {"populate_by_name": True, "extra": "allow"}


class XPSeasonWeek(BaseModel):
    """A week within an XP season."""

    week: int
    start_date: datetime = Field(..., alias="startDate")
    end_date: datetime = Field(..., alias="endDate")

    model_config = {"populate_by_name": True, "extra": "allow"}


class XPTip(BaseModel):
    """An XP tip transaction."""

    id: int
    sender_profile_id: int = Field(..., alias="senderProfileId")
    receiver_profile_id: int = Field(..., alias="receiverProfileId")
    amount: int
    created_at: datetime | None = Field(None, alias="createdAt")

    # Associated user profiles
    sender: dict | None = None
    receiver: dict | None = None

    model_config = {"populate_by_name": True, "extra": "allow"}


class XPTipStats(BaseModel):
    """XP tip statistics."""

    total_sent: int = Field(0, alias="totalSent")
    total_received: int = Field(0, alias="totalReceived")

    model_config = {"populate_by_name": True, "extra": "allow"}

    @property
    def net_tips(self) -> int:
        """Net XP from tips (received - sent)."""
        return self.total_received - self.total_sent


class XPDecision(BaseModel):
    """A user's XP decision for a season."""

    decision_type: DecisionType = Field(..., alias="decisionType")
    delegations: list[dict] | None = None
    created_at: datetime | None = Field(None, alias="createdAt")
    updated_at: datetime | None = Field(None, alias="updatedAt")

    model_config = {"populate_by_name": True, "extra": "allow"}


class XPDecisionMetadata(BaseModel):
    """Metadata about XP decisions."""

    deadline: datetime | None = None
    spend_percentage: float = Field(0.0, alias="spendPercentage")
    delegate_percentage: float = Field(0.0, alias="delegatePercentage")
    validator_cap: int = Field(0, alias="validatorCap")
    inactivity_penalty: float = Field(0.0, alias="inactivityPenalty")

    model_config = {"populate_by_name": True, "extra": "allow"}


class XPValidator(BaseModel):
    """A validator for XP delegation."""

    profile_id: int = Field(..., alias="profileId")
    display_name: str | None = Field(None, alias="displayName")
    username: str | None = None
    avatar_url: str | None = Field(None, alias="avatarUrl")
    xp_capacity: int = Field(0, alias="xpCapacity")
    xp_delegated: int = Field(0, alias="xpDelegated")

    model_config = {"populate_by_name": True, "extra": "allow"}

    @property
    def available_capacity(self) -> int:
        """Get available delegation capacity."""
        return max(0, self.xp_capacity - self.xp_delegated)

    @property
    def is_at_capacity(self) -> bool:
        """Check if validator is at capacity."""
        return self.xp_delegated >= self.xp_capacity
