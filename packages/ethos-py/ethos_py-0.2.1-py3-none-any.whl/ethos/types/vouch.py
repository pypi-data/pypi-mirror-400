"""
Vouch model for Ethos vouching relationships.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class Vouch(BaseModel):
    """
    A vouch relationship on Ethos Network.

    A vouch represents one user staking ETH on another user's reputation,
    signaling trust and confidence in that person.
    """

    id: int

    # Relationship
    author_profile_id: int = Field(..., alias="authorProfileId")
    target_profile_id: int = Field(..., alias="subjectProfileId")

    # Staking details
    staked: bool = True
    archived: bool = False
    unhealthy: bool = False

    # Amount (in wei)
    balance: str = "0"  # String because wei can be very large

    # Activity tracking
    activity_checkpoints: dict = Field(default_factory=dict, alias="activityCheckpoints")

    # Timestamps
    created_at: datetime | None = Field(None, alias="createdAt")
    updated_at: datetime | None = Field(None, alias="updatedAt")

    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }

    @property
    def amount_wei(self) -> int:
        """Get the vouch amount in wei as an integer."""
        return int(self.balance)

    @property
    def amount_eth(self) -> float:
        """Get the vouch amount in ETH."""
        return self.amount_wei / 1e18

    @property
    def is_active(self) -> bool:
        """Check if the vouch is currently active."""
        return self.staked and not self.archived

    @property
    def voucher_id(self) -> int:
        """Alias for author_profile_id."""
        return self.author_profile_id

    @property
    def target_id(self) -> int:
        """Alias for target_profile_id."""
        return self.target_profile_id
