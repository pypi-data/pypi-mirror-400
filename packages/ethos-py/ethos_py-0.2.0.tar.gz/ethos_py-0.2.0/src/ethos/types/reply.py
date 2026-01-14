"""
Reply types for Ethos API.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

ReplyContractType = Literal[
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


class ReplyAuthor(BaseModel):
    """Author of a reply."""

    id: int
    profile_id: int | None = Field(None, alias="profileId")
    display_name: str | None = Field(None, alias="displayName")
    username: str | None = None
    avatar_url: str | None = Field(None, alias="avatarUrl")
    score: int = 0

    model_config = {"populate_by_name": True, "extra": "allow"}


class Reply(BaseModel):
    """
    A reply on Ethos Network.

    Replies are comments on activities like reviews, vouches, etc.
    """

    id: int
    contract_type: str = Field(..., alias="contractType")
    target_contract: str | None = Field(None, alias="targetContract")
    parent_id: int = Field(..., alias="parentId")
    author_profile_id: int = Field(..., alias="authorProfileId")
    content: str
    metadata: dict | None = None
    url: str | None = None

    # Nested author
    user: ReplyAuthor | None = None

    # Timestamps
    created_at: datetime | None = Field(None, alias="createdAt")

    model_config = {"populate_by_name": True, "extra": "allow"}

    @property
    def author(self) -> ReplyAuthor | None:
        """Alias for user field."""
        return self.user

    @property
    def is_review_reply(self) -> bool:
        """Check if this is a reply to a review."""
        return self.contract_type == "review"

    @property
    def is_vouch_reply(self) -> bool:
        """Check if this is a reply to a vouch."""
        return self.contract_type == "vouch"
