"""
Invitation types for Ethos API.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

InvitationStatus = Literal["ACCEPTED", "INVITED", "ACCEPTED_OTHER_INVITATION"]


class InviterProfile(BaseModel):
    """Profile of an inviter."""

    id: int
    profile_id: int | None = Field(None, alias="profileId")
    display_name: str | None = Field(None, alias="displayName")
    username: str | None = None
    avatar_url: str | None = Field(None, alias="avatarUrl")
    score: int = 0

    model_config = {"populate_by_name": True, "extra": "allow"}


class Invitation(BaseModel):
    """
    An invitation on Ethos Network.

    Invitations are used to invite new users to join Ethos,
    creating a tree of invitation relationships.
    """

    id: int
    sender_profile_id: int = Field(..., alias="senderProfileId")
    invitee_address: str | None = Field(None, alias="inviteeAddress")
    status: str = "INVITED"

    # Score impact information
    score_impact: int | None = Field(None, alias="scoreImpact")

    # Nested inviter profile
    sender: InviterProfile | None = None
    inviter: InviterProfile | None = None  # Alias

    # Timestamps
    created_at: datetime | None = Field(None, alias="createdAt")
    accepted_at: datetime | None = Field(None, alias="acceptedAt")

    model_config = {"populate_by_name": True, "extra": "allow"}

    @property
    def is_accepted(self) -> bool:
        """Check if invitation has been accepted."""
        return self.status == "ACCEPTED"

    @property
    def is_pending(self) -> bool:
        """Check if invitation is pending."""
        return self.status == "INVITED"


class InvitationTreeNode(BaseModel):
    """A node in the invitation tree."""

    profile_id: int = Field(..., alias="profileId")
    invitee_profile_id: int | None = Field(None, alias="inviteeProfileId")
    depth: int = 0

    # User info
    user: InviterProfile | None = None

    # Children in tree
    children: list[InvitationTreeNode] = Field(default_factory=list)

    model_config = {"populate_by_name": True, "extra": "allow"}


class InvitationEligibility(BaseModel):
    """Eligibility check result for sending an invitation."""

    can_invite: bool = Field(..., alias="canInvite")
    address: str | None = None
    reason: str | None = None

    model_config = {"populate_by_name": True, "extra": "allow"}
