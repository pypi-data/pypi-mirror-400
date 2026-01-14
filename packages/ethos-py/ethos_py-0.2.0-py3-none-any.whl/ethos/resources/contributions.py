"""
Contributions resource for Ethos API.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ethos.resources.base import AsyncBaseResource, BaseResource
from ethos.types.contribution import (
    ContributionDay,
    ContributionHistory,
    ForgiveResult,
)

if TYPE_CHECKING:
    pass


class Contributions(BaseResource[ContributionDay]):
    """
    Contributions API resource.

    Access user contribution history. Requires authentication.
    """

    _path = "/contributions"
    _model = ContributionDay

    def get_history(self, duration: str = "1y") -> ContributionHistory:
        """
        Get contribution history for the authenticated user.

        Args:
            duration: Time duration (e.g., "1y", "6m", "30d")

        Returns:
            Contribution history
        """
        response = self._http.get(f"{self._path}/history", params={"duration": duration})
        return ContributionHistory.model_validate(response)

    def get_days(self, duration: str = "1y") -> list[ContributionDay]:
        """
        Get contribution days as a list.

        Args:
            duration: Time duration

        Returns:
            List of contribution days
        """
        history = self.get_history(duration)
        return history.history

    def forgive_day(self, userkey: str) -> ForgiveResult:
        """
        Forgive a missed contribution day for a user.

        Requires admin authentication.

        Args:
            userkey: The user's userkey

        Returns:
            Result of the forgive operation
        """
        response = self._http.post(f"{self._path}/{userkey}/forgive", json={})
        return ForgiveResult.model_validate(response)


class AsyncContributions(AsyncBaseResource[ContributionDay]):
    """Async Contributions API resource."""

    _path = "/contributions"
    _model = ContributionDay

    async def get_history(self, duration: str = "1y") -> ContributionHistory:
        """Get contribution history for the authenticated user."""
        response = await self._http.get(f"{self._path}/history", params={"duration": duration})
        return ContributionHistory.model_validate(response)

    async def get_days(self, duration: str = "1y") -> list[ContributionDay]:
        """Get contribution days as a list."""
        history = await self.get_history(duration)
        return history.history

    async def forgive_day(self, userkey: str) -> ForgiveResult:
        """Forgive a missed contribution day for a user."""
        response = await self._http.post(f"{self._path}/{userkey}/forgive", json={})
        return ForgiveResult.model_validate(response)
