"""
Activity model for Ethos on-chain activities.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

ActivityType = Literal[
    "vouch",
    "unvouch",
    "review",
    "attestation",
    "invite_accepted",
    "profile_created",
    "score_updated",
]


class Activity(BaseModel):
    """
    An on-chain activity on Ethos Network.

    Activities represent all actions taken on the network,
    including vouches, reviews, attestations, and more.
    """

    id: int

    # Activity type
    type: str

    # Actor
    author_profile_id: int | None = Field(None, alias="authorProfileId")
    target_profile_id: int | None = Field(None, alias="subjectProfileId")

    # Transaction details
    tx_hash: str | None = Field(None, alias="txHash")
    block_number: int | None = Field(None, alias="blockNumber")

    # Event data (varies by activity type)
    data: dict[str, Any] = Field(default_factory=dict)

    # Timestamps
    created_at: datetime | None = Field(None, alias="createdAt")

    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }

    @property
    def is_vouch(self) -> bool:
        """Check if this is a vouch activity."""
        return self.type == "vouch"

    @property
    def is_review(self) -> bool:
        """Check if this is a review activity."""
        return self.type == "review"

    @property
    def actor_id(self) -> int | None:
        """Alias for author_profile_id."""
        return self.author_profile_id

    @property
    def etherscan_url(self) -> str | None:
        """Get Etherscan URL for this transaction."""
        if self.tx_hash:
            return f"https://basescan.org/tx/{self.tx_hash}"
        return None
