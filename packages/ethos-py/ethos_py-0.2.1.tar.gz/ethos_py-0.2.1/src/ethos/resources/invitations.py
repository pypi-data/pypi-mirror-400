"""
Invitations resource for Ethos API.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import TYPE_CHECKING, Any

from ethos.resources.base import AsyncBaseResource, BaseResource
from ethos.types.invitation import (
    Invitation,
    InvitationEligibility,
    InvitationStatus,
    InvitationTreeNode,
)

if TYPE_CHECKING:
    pass


class Invitations(BaseResource[Invitation]):
    """
    Invitations API resource.

    Access invitation data and manage invitations.
    """

    _path = "/invitations"
    _model = Invitation

    def list(
        self,
        sender_profile_id: int | None = None,
        status: InvitationStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Iterator[Invitation]:
        """
        List invitations with optional filtering.

        Args:
            sender_profile_id: Filter by sender
            status: Filter by status
            limit: Page size
            offset: Starting offset

        Yields:
            Invitation objects
        """
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if sender_profile_id is not None:
            params["senderProfileId"] = sender_profile_id
        if status is not None:
            params["status"] = status

        yield from self._paginate(self._path, params=params, limit=limit)

    def check_eligibility(
        self,
        address_or_ens: str,
        sender_profile_id: int | None = None,
    ) -> InvitationEligibility:
        """
        Check if an address can be invited.

        Args:
            address_or_ens: Ethereum address or ENS name
            sender_profile_id: Optional sender profile ID

        Returns:
            Eligibility check result
        """
        params: dict[str, Any] = {"addressOrEns": address_or_ens}
        if sender_profile_id is not None:
            params["senderProfileId"] = sender_profile_id

        response = self._http.get(f"{self._path}/check", params=params)
        return InvitationEligibility.model_validate(response)

    def get_pending_for_address(self, address: str) -> list[Invitation]:
        """
        Get pending invitations for an address.

        Args:
            address: The Ethereum address

        Returns:
            List of pending invitations
        """
        response = self._http.get(f"{self._path}/pending/{address}")
        if isinstance(response, list):
            return self._parse_list(response)
        return []

    def get_invitation_tree(
        self,
        sender_profile_id: int,
        depth: int = 3,
        limit: int = 50,
        offset: int = 0,
    ) -> list[InvitationTreeNode]:
        """
        Get the invitation tree for a user.

        Args:
            sender_profile_id: The sender's profile ID
            depth: Maximum tree depth (max 5)
            limit: Maximum nodes
            offset: Pagination offset

        Returns:
            List of invitation tree nodes
        """
        response = self._http.get(
            f"{self._path}/accepted/{sender_profile_id}/tree",
            params={"depth": min(depth, 5), "limit": limit, "offset": offset},
        )
        values = response.get("values", []) if isinstance(response, dict) else response
        return [InvitationTreeNode.model_validate(n) for n in values]

    def by_sender(self, sender_profile_id: int) -> list[Invitation]:
        """Get all invitations sent by a profile."""
        return list(self.list(sender_profile_id=sender_profile_id))

    def pending(self) -> list[Invitation]:
        """Get all pending invitations."""
        return list(self.list(status="INVITED"))

    def accepted(self) -> list[Invitation]:
        """Get all accepted invitations."""
        return list(self.list(status="ACCEPTED"))


class AsyncInvitations(AsyncBaseResource[Invitation]):
    """Async Invitations API resource."""

    _path = "/invitations"
    _model = Invitation

    async def list(
        self,
        sender_profile_id: int | None = None,
        status: InvitationStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> AsyncIterator[Invitation]:
        """List invitations with optional filtering."""
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if sender_profile_id is not None:
            params["senderProfileId"] = sender_profile_id
        if status is not None:
            params["status"] = status

        async for invitation in self._paginate(self._path, params=params, limit=limit):
            yield invitation

    async def check_eligibility(
        self,
        address_or_ens: str,
        sender_profile_id: int | None = None,
    ) -> InvitationEligibility:
        """Check if an address can be invited."""
        params: dict[str, Any] = {"addressOrEns": address_or_ens}
        if sender_profile_id is not None:
            params["senderProfileId"] = sender_profile_id

        response = await self._http.get(f"{self._path}/check", params=params)
        return InvitationEligibility.model_validate(response)

    async def get_pending_for_address(self, address: str) -> list[Invitation]:
        """Get pending invitations for an address."""
        response = await self._http.get(f"{self._path}/pending/{address}")
        if isinstance(response, list):
            return self._parse_list(response)
        return []

    async def get_invitation_tree(
        self,
        sender_profile_id: int,
        depth: int = 3,
        limit: int = 50,
        offset: int = 0,
    ) -> list[InvitationTreeNode]:
        """Get the invitation tree for a user."""
        response = await self._http.get(
            f"{self._path}/accepted/{sender_profile_id}/tree",
            params={"depth": min(depth, 5), "limit": limit, "offset": offset},
        )
        values = response.get("values", []) if isinstance(response, dict) else response
        return [InvitationTreeNode.model_validate(n) for n in values]

    async def by_sender(self, sender_profile_id: int) -> list[Invitation]:
        """Get all invitations sent by a profile."""
        invitations = []
        async for inv in self.list(sender_profile_id=sender_profile_id):
            invitations.append(inv)
        return invitations
