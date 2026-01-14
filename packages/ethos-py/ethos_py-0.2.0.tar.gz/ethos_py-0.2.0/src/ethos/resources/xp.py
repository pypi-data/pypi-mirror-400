"""
XP (Experience Points) resource for Ethos API.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ethos.resources.base import AsyncBaseResource, BaseResource
from ethos.types.xp import (
    XPDecision,
    XPDecisionMetadata,
    XPHistoryEntry,
    XPSeason,
    XPSeasonWeek,
    XPTip,
    XPTipStats,
    XPValidator,
    XPWeeklyData,
)

if TYPE_CHECKING:
    pass


class XP(BaseResource[XPHistoryEntry]):
    """
    XP (Experience Points) API resource.

    Access XP data, history, tips, seasons, and decisions.
    """

    _path = "/xp"
    _model = XPHistoryEntry

    def get_total(self, userkey: str) -> int:
        """
        Get total XP for a user across all seasons.

        Args:
            userkey: The user's userkey

        Returns:
            Total XP amount
        """
        response = self._http.get(f"{self._path}/user/{userkey}")
        if isinstance(response, int):
            return response
        return response.get("total", response.get("xp", 0))

    def get_season_total(self, userkey: str, season_id: int) -> int:
        """
        Get XP for a user in a specific season.

        Args:
            userkey: The user's userkey
            season_id: The season ID

        Returns:
            Season XP amount
        """
        response = self._http.get(f"{self._path}/user/{userkey}/season/{season_id}")
        if isinstance(response, int):
            return response
        return response.get("total", response.get("xp", 0))

    def get_weekly(self, userkey: str, season_id: int) -> list[XPWeeklyData]:
        """
        Get weekly XP breakdown for a user in a season.

        Args:
            userkey: The user's userkey
            season_id: The season ID

        Returns:
            List of weekly XP data
        """
        response = self._http.get(f"{self._path}/user/{userkey}/season/{season_id}/weekly")
        if isinstance(response, list):
            return [XPWeeklyData.model_validate(w) for w in response]
        return []

    def get_leaderboard_rank(self, userkey: str) -> int:
        """
        Get a user's XP leaderboard rank.

        Args:
            userkey: The user's userkey

        Returns:
            Leaderboard rank (1-indexed)
        """
        response = self._http.get(f"{self._path}/user/{userkey}/leaderboard-rank")
        if isinstance(response, int):
            return response
        return response.get("rank", 0)

    def get_history(
        self,
        userkey: str,
        season_id: int | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[XPHistoryEntry]:
        """
        Get XP history for a user.

        Args:
            userkey: The user's userkey
            season_id: Optional season ID filter
            limit: Maximum entries
            offset: Pagination offset

        Returns:
            List of XP history entries
        """
        params: dict[str, Any] = {
            "userkey": userkey,
            "limit": limit,
            "offset": offset,
        }
        if season_id is not None:
            params["seasonId"] = season_id

        response = self._http.get(f"{self._path}/history", params=params)
        values = response.get("values", []) if isinstance(response, dict) else response
        return [XPHistoryEntry.model_validate(e) for e in values]

    def get_seasons(self) -> tuple[list[XPSeason], XPSeason | None]:
        """
        Get all XP seasons and the current season.

        Returns:
            Tuple of (all seasons, current season)
        """
        response = self._http.get(f"{self._path}/seasons")
        seasons = [XPSeason.model_validate(s) for s in response.get("seasons", [])]
        current = None
        if response.get("current"):
            current = XPSeason.model_validate(response["current"])
        return seasons, current

    def get_season_weeks(self, season_id: int) -> list[XPSeasonWeek]:
        """
        Get weeks for a season.

        Args:
            season_id: The season ID

        Returns:
            List of season weeks
        """
        response = self._http.get(f"{self._path}/season/{season_id}/weeks")
        if isinstance(response, list):
            return [XPSeasonWeek.model_validate(w) for w in response]
        return []

    # Tip methods (require authentication)
    def get_tips_sent(self, limit: int = 50, offset: int = 0) -> list[XPTip]:
        """Get tips sent by authenticated user."""
        response = self._http.get(
            f"{self._path}/tips/sent", params={"limit": limit, "offset": offset}
        )
        values = response.get("values", []) if isinstance(response, dict) else response
        return [XPTip.model_validate(t) for t in values]

    def get_tips_received(self, limit: int = 50, offset: int = 0) -> list[XPTip]:
        """Get tips received by authenticated user."""
        response = self._http.get(
            f"{self._path}/tips/received", params={"limit": limit, "offset": offset}
        )
        values = response.get("values", []) if isinstance(response, dict) else response
        return [XPTip.model_validate(t) for t in values]

    def get_tip_stats(self) -> XPTipStats:
        """Get tip statistics for authenticated user."""
        response = self._http.get(f"{self._path}/tips/stats")
        return XPTipStats.model_validate(response)

    # Decision methods (require authentication)
    def get_decision(self) -> XPDecision | None:
        """Get authenticated user's XP decision."""
        response = self._http.get(f"{self._path}/decision")
        if response:
            return XPDecision.model_validate(response)
        return None

    def get_decision_metadata(self) -> XPDecisionMetadata:
        """Get XP decision metadata (deadlines, percentages, etc.)."""
        response = self._http.get(f"{self._path}/decision/metadata")
        return XPDecisionMetadata.model_validate(response)

    def get_validators(self) -> list[XPValidator]:
        """Get available validators for XP delegation."""
        response = self._http.get(f"{self._path}/validators")
        if isinstance(response, list):
            return [XPValidator.model_validate(v) for v in response]
        return []


class AsyncXP(AsyncBaseResource[XPHistoryEntry]):
    """Async XP API resource."""

    _path = "/xp"
    _model = XPHistoryEntry

    async def get_total(self, userkey: str) -> int:
        """Get total XP for a user."""
        response = await self._http.get(f"{self._path}/user/{userkey}")
        if isinstance(response, int):
            return response
        return response.get("total", response.get("xp", 0))

    async def get_season_total(self, userkey: str, season_id: int) -> int:
        """Get XP for a user in a season."""
        response = await self._http.get(f"{self._path}/user/{userkey}/season/{season_id}")
        if isinstance(response, int):
            return response
        return response.get("total", response.get("xp", 0))

    async def get_weekly(self, userkey: str, season_id: int) -> list[XPWeeklyData]:
        """Get weekly XP breakdown."""
        response = await self._http.get(f"{self._path}/user/{userkey}/season/{season_id}/weekly")
        if isinstance(response, list):
            return [XPWeeklyData.model_validate(w) for w in response]
        return []

    async def get_leaderboard_rank(self, userkey: str) -> int:
        """Get user's leaderboard rank."""
        response = await self._http.get(f"{self._path}/user/{userkey}/leaderboard-rank")
        if isinstance(response, int):
            return response
        return response.get("rank", 0)

    async def get_history(
        self,
        userkey: str,
        season_id: int | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[XPHistoryEntry]:
        """Get XP history for a user."""
        params: dict[str, Any] = {
            "userkey": userkey,
            "limit": limit,
            "offset": offset,
        }
        if season_id is not None:
            params["seasonId"] = season_id

        response = await self._http.get(f"{self._path}/history", params=params)
        values = response.get("values", []) if isinstance(response, dict) else response
        return [XPHistoryEntry.model_validate(e) for e in values]

    async def get_seasons(self) -> tuple[list[XPSeason], XPSeason | None]:
        """Get all XP seasons and current season."""
        response = await self._http.get(f"{self._path}/seasons")
        seasons = [XPSeason.model_validate(s) for s in response.get("seasons", [])]
        current = None
        if response.get("current"):
            current = XPSeason.model_validate(response["current"])
        return seasons, current

    async def get_season_weeks(self, season_id: int) -> list[XPSeasonWeek]:
        """Get weeks for a season."""
        response = await self._http.get(f"{self._path}/season/{season_id}/weeks")
        if isinstance(response, list):
            return [XPSeasonWeek.model_validate(w) for w in response]
        return []

    async def get_tips_sent(self, limit: int = 50, offset: int = 0) -> list[XPTip]:
        """Get tips sent by authenticated user."""
        response = await self._http.get(
            f"{self._path}/tips/sent", params={"limit": limit, "offset": offset}
        )
        values = response.get("values", []) if isinstance(response, dict) else response
        return [XPTip.model_validate(t) for t in values]

    async def get_tips_received(self, limit: int = 50, offset: int = 0) -> list[XPTip]:
        """Get tips received by authenticated user."""
        response = await self._http.get(
            f"{self._path}/tips/received", params={"limit": limit, "offset": offset}
        )
        values = response.get("values", []) if isinstance(response, dict) else response
        return [XPTip.model_validate(t) for t in values]

    async def get_tip_stats(self) -> XPTipStats:
        """Get tip statistics."""
        response = await self._http.get(f"{self._path}/tips/stats")
        return XPTipStats.model_validate(response)

    async def get_decision(self) -> XPDecision | None:
        """Get user's XP decision."""
        response = await self._http.get(f"{self._path}/decision")
        if response:
            return XPDecision.model_validate(response)
        return None

    async def get_decision_metadata(self) -> XPDecisionMetadata:
        """Get XP decision metadata."""
        response = await self._http.get(f"{self._path}/decision/metadata")
        return XPDecisionMetadata.model_validate(response)

    async def get_validators(self) -> list[XPValidator]:
        """Get available validators."""
        response = await self._http.get(f"{self._path}/validators")
        if isinstance(response, list):
            return [XPValidator.model_validate(v) for v in response]
        return []
