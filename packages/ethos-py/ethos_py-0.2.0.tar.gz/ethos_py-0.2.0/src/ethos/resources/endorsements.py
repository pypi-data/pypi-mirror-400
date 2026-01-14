"""
Endorsements resource for Ethos API.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ethos.resources.base import AsyncBaseResource, BaseResource
from ethos.types.endorsement import Endorsement, EndorsementSummary

if TYPE_CHECKING:
    pass


class EndorsementsResponse:
    """Response from endorsements endpoint with both data and summary."""

    def __init__(
        self,
        endorsements: list[Endorsement],
        summary: EndorsementSummary,
        total: int,
        limit: int,
        offset: int,
    ):
        self.endorsements = endorsements
        self.summary = summary
        self.total = total
        self.limit = limit
        self.offset = offset

    def __iter__(self):
        return iter(self.endorsements)

    def __len__(self):
        return len(self.endorsements)


class Endorsements(BaseResource[Endorsement]):
    """
    Endorsements API resource.

    Access endorsement data showing trust relationships between users.
    Requires authentication for viewer-specific context.
    """

    _path = "/endorsements"
    _model = Endorsement

    def get_for_user(
        self,
        target_userkey: str,
        limit: int = 50,
        offset: int = 0,
    ) -> EndorsementsResponse:
        """
        Get endorsers of a target user that the viewer knows.

        This endpoint requires authentication to provide viewer-specific
        connection context.

        Args:
            target_userkey: The target user's userkey
            limit: Maximum results (max 50)
            offset: Pagination offset

        Returns:
            EndorsementsResponse with endorsements and summary
        """
        response = self._http.get(
            f"{self._path}/{target_userkey}",
            params={"limit": limit, "offset": offset},
        )

        endorsements = [Endorsement.model_validate(e) for e in response.get("values", [])]
        summary = EndorsementSummary.model_validate(response.get("summary", {}))

        return EndorsementsResponse(
            endorsements=endorsements,
            summary=summary,
            total=response.get("total", 0),
            limit=response.get("limit", limit),
            offset=response.get("offset", offset),
        )

    def list_for_user(
        self,
        target_userkey: str,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Endorsement]:
        """
        Get endorsements for a user (simplified version).

        Args:
            target_userkey: The target user's userkey
            limit: Maximum results
            offset: Pagination offset

        Returns:
            List of endorsements
        """
        response = self.get_for_user(target_userkey, limit, offset)
        return response.endorsements


class AsyncEndorsements(AsyncBaseResource[Endorsement]):
    """Async Endorsements API resource."""

    _path = "/endorsements"
    _model = Endorsement

    async def get_for_user(
        self,
        target_userkey: str,
        limit: int = 50,
        offset: int = 0,
    ) -> EndorsementsResponse:
        """
        Get endorsers of a target user that the viewer knows.

        Args:
            target_userkey: The target user's userkey
            limit: Maximum results (max 50)
            offset: Pagination offset

        Returns:
            EndorsementsResponse with endorsements and summary
        """
        response = await self._http.get(
            f"{self._path}/{target_userkey}",
            params={"limit": limit, "offset": offset},
        )

        endorsements = [Endorsement.model_validate(e) for e in response.get("values", [])]
        summary = EndorsementSummary.model_validate(response.get("summary", {}))

        return EndorsementsResponse(
            endorsements=endorsements,
            summary=summary,
            total=response.get("total", 0),
            limit=response.get("limit", limit),
            offset=response.get("offset", offset),
        )

    async def list_for_user(
        self,
        target_userkey: str,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Endorsement]:
        """Get endorsements for a user (simplified version)."""
        response = await self.get_for_user(target_userkey, limit, offset)
        return response.endorsements
