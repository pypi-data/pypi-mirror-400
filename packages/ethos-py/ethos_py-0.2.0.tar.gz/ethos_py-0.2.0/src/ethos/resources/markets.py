"""
Markets resource for Ethos API.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import TYPE_CHECKING, Any

from ethos.resources.base import AsyncBaseResource, BaseResource
from ethos.types.market import Market

if TYPE_CHECKING:
    pass


class Markets(BaseResource[Market]):
    """
    Markets API resource.

    Access reputation markets for trading trust/distrust.
    """

    _path = "/markets"
    _model = Market

    def get(self, market_id: int) -> Market:
        """
        Get a market by ID.

        Args:
            market_id: The market ID

        Returns:
            The market
        """
        response = self._http.get(f"{self._path}/{market_id}")
        return self._parse_item(response)

    def get_by_profile(self, profile_id: int) -> Market:
        """
        Get the market for a profile.

        Args:
            profile_id: The profile ID

        Returns:
            The market for that profile
        """
        response = self._http.get(f"{self._path}/profile/{profile_id}")
        return self._parse_item(response)

    def list(
        self,
        is_active: bool | None = None,
        order_by: str | None = None,
        limit: int = 100,
    ) -> Iterator[Market]:
        """
        List markets with optional filtering.

        Args:
            is_active: Filter by active status
            order_by: Sort order (e.g., "totalVolume", "trustPrice")
            limit: Page size

        Yields:
            Market objects
        """
        params: dict[str, Any] = {}

        if is_active is not None:
            params["isActive"] = is_active
        if order_by is not None:
            params["orderBy"] = order_by

        yield from self._paginate(self._path, params=params, limit=limit)

    def top_by_volume(self, limit: int = 20) -> list[Market]:
        """
        Get top markets by trading volume.

        Args:
            limit: Number of markets to return

        Returns:
            Markets sorted by volume
        """
        markets = list(self.list(order_by="totalVolume", limit=limit))
        return sorted(markets, key=lambda m: m.total_volume, reverse=True)[:limit]

    def most_trusted(self, limit: int = 20) -> list[Market]:
        """
        Get markets with highest trust prices.

        Args:
            limit: Number of markets to return

        Returns:
            Markets sorted by trust price
        """
        markets = list(self.list(limit=limit * 2))  # Get extra to sort
        return sorted(markets, key=lambda m: m.trust_price, reverse=True)[:limit]

    def most_distrusted(self, limit: int = 20) -> list[Market]:
        """
        Get markets with highest distrust prices.

        Args:
            limit: Number of markets to return

        Returns:
            Markets sorted by distrust price
        """
        markets = list(self.list(limit=limit * 2))
        return sorted(markets, key=lambda m: m.distrust_price, reverse=True)[:limit]


class AsyncMarkets(AsyncBaseResource[Market]):
    """Async Markets API resource."""

    _path = "/markets"
    _model = Market

    async def get(self, market_id: int) -> Market:
        """Get a market by ID."""
        response = await self._http.get(f"{self._path}/{market_id}")
        return self._parse_item(response)

    async def get_by_profile(self, profile_id: int) -> Market:
        """Get the market for a profile."""
        response = await self._http.get(f"{self._path}/profile/{profile_id}")
        return self._parse_item(response)

    async def list(
        self,
        is_active: bool | None = None,
        order_by: str | None = None,
        limit: int = 100,
    ) -> AsyncIterator[Market]:
        """List markets with optional filtering."""
        params: dict[str, Any] = {}

        if is_active is not None:
            params["isActive"] = is_active
        if order_by is not None:
            params["orderBy"] = order_by

        async for market in self._paginate(self._path, params=params, limit=limit):
            yield market

    async def top_by_volume(self, limit: int = 20) -> list[Market]:
        """Get top markets by trading volume."""
        markets = []
        async for market in self.list(order_by="totalVolume", limit=limit):
            markets.append(market)
        return sorted(markets, key=lambda m: m.total_volume, reverse=True)[:limit]
