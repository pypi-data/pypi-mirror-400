"""
Scores resource for Ethos API.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ethos.resources.base import AsyncBaseResource, BaseResource
from ethos.types.score import Score

if TYPE_CHECKING:
    pass


class Scores(BaseResource[Score]):
    """
    Scores API resource.

    Access credibility scores for profiles.
    """

    _path = "/score"
    _model = Score

    def get(self, address: str) -> Score:
        """
        Get the credibility score for an address.

        Args:
            address: Ethereum address (0x...)

        Returns:
            The score details
        """
        response = self._http.get(f"{self._path}/{address}")
        return self._parse_item(response)

    def get_by_profile(self, profile_id: int) -> Score:
        """
        Get the credibility score for a profile ID.

        Args:
            profile_id: The profile ID

        Returns:
            The score details
        """
        response = self._http.get(f"{self._path}/profile/{profile_id}")
        return self._parse_item(response)

    def breakdown(self, address: str) -> Score:
        """
        Get detailed score breakdown for an address.

        Args:
            address: Ethereum address

        Returns:
            Score with detailed breakdown
        """
        response = self._http.get(f"{self._path}/{address}/breakdown")
        return self._parse_item(response)


class AsyncScores(AsyncBaseResource[Score]):
    """Async Scores API resource."""

    _path = "/score"
    _model = Score

    async def get(self, address: str) -> Score:
        """Get the credibility score for an address."""
        response = await self._http.get(f"{self._path}/{address}")
        return self._parse_item(response)

    async def get_by_profile(self, profile_id: int) -> Score:
        """Get the credibility score for a profile ID."""
        response = await self._http.get(f"{self._path}/profile/{profile_id}")
        return self._parse_item(response)

    async def breakdown(self, address: str) -> Score:
        """Get detailed score breakdown for an address."""
        response = await self._http.get(f"{self._path}/{address}/breakdown")
        return self._parse_item(response)
