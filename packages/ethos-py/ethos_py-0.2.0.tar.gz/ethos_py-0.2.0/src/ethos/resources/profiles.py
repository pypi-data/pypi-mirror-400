"""
Profiles resource for Ethos API.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import TYPE_CHECKING, Any

from ethos.resources.base import AsyncBaseResource, BaseResource
from ethos.types.profile import Profile

if TYPE_CHECKING:
    pass


class Profiles(BaseResource[Profile]):
    """
    Profiles API resource.

    Access Ethos user profiles by ID, address, or Twitter handle.
    """

    _path = "/profiles"
    _model = Profile

    def get(self, profile_id: int) -> Profile:
        """
        Get a profile by ID.

        Args:
            profile_id: The Ethos profile ID

        Returns:
            The profile
        """
        response = self._http.get(f"{self._path}/{profile_id}")
        return self._parse_item(response)

    def get_by_address(self, address: str) -> Profile:
        """
        Get a profile by Ethereum address.

        Args:
            address: The Ethereum address (0x...)

        Returns:
            The profile
        """
        response = self._http.get(f"{self._path}/address/{address}")
        return self._parse_item(response)

    def get_by_twitter(self, handle: str) -> Profile:
        """
        Get a profile by Twitter/X handle.

        Args:
            handle: Twitter username (without @)

        Returns:
            The profile
        """
        # Remove @ if present
        handle = handle.lstrip("@")
        userkey = f"x.com/user/{handle}"
        response = self._http.get(f"{self._path}/userkey/{userkey}")
        return self._parse_item(response)

    def get_by_userkey(self, userkey: str) -> Profile:
        """
        Get a profile by userkey.

        Userkeys are identifiers like "x.com/user/username" or
        "farcaster.xyz/user/fid/12345".

        Args:
            userkey: The userkey identifier

        Returns:
            The profile
        """
        response = self._http.get(f"{self._path}/userkey/{userkey}")
        return self._parse_item(response)

    def search(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Profile]:
        """
        Search profiles by name or username.

        Args:
            query: Search query
            limit: Maximum results to return
            offset: Results offset for pagination

        Returns:
            List of matching profiles
        """
        response = self._http.get(
            f"{self._path}/search",
            params={
                "query": query,
                "limit": limit,
                "offset": offset,
            },
        )

        if isinstance(response, list):
            return self._parse_list(response)
        return self._parse_list(response.get("values", response.get("data", [])))

    def list(
        self,
        limit: int = 100,
        offset: int = 0,
        order_by: str | None = None,
    ) -> Iterator[Profile]:
        """
        List all profiles with pagination.

        Args:
            limit: Page size
            offset: Starting offset
            order_by: Sort order (e.g., "score", "createdAt")

        Yields:
            Profile objects
        """
        params: dict[str, Any] = {}
        if order_by:
            params["orderBy"] = order_by

        yield from self._paginate(self._path, params=params, limit=limit)

    def recent(self, limit: int = 20) -> list[Profile]:
        """
        Get recently created profiles.

        Args:
            limit: Maximum results

        Returns:
            List of recent profiles
        """
        response = self._http.get(
            f"{self._path}/recent",
            params={"limit": limit},
        )

        if isinstance(response, list):
            return self._parse_list(response)
        return self._parse_list(response.get("values", response.get("data", [])))


class AsyncProfiles(AsyncBaseResource[Profile]):
    """Async Profiles API resource."""

    _path = "/profiles"
    _model = Profile

    async def get(self, profile_id: int) -> Profile:
        """Get a profile by ID."""
        response = await self._http.get(f"{self._path}/{profile_id}")
        return self._parse_item(response)

    async def get_by_address(self, address: str) -> Profile:
        """Get a profile by Ethereum address."""
        response = await self._http.get(f"{self._path}/address/{address}")
        return self._parse_item(response)

    async def get_by_twitter(self, handle: str) -> Profile:
        """Get a profile by Twitter/X handle."""
        handle = handle.lstrip("@")
        userkey = f"x.com/user/{handle}"
        response = await self._http.get(f"{self._path}/userkey/{userkey}")
        return self._parse_item(response)

    async def get_by_userkey(self, userkey: str) -> Profile:
        """Get a profile by userkey."""
        response = await self._http.get(f"{self._path}/userkey/{userkey}")
        return self._parse_item(response)

    async def search(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Profile]:
        """Search profiles."""
        response = await self._http.get(
            f"{self._path}/search",
            params={
                "query": query,
                "limit": limit,
                "offset": offset,
            },
        )

        if isinstance(response, list):
            return self._parse_list(response)
        return self._parse_list(response.get("values", response.get("data", [])))

    async def list(
        self,
        limit: int = 100,
        offset: int = 0,
        order_by: str | None = None,
    ) -> AsyncIterator[Profile]:
        """List all profiles with pagination."""
        params: dict[str, Any] = {}
        if order_by:
            params["orderBy"] = order_by

        async for profile in self._paginate(self._path, params=params, limit=limit):
            yield profile

    async def recent(self, limit: int = 20) -> list[Profile]:
        """Get recently created profiles."""
        response = await self._http.get(
            f"{self._path}/recent",
            params={"limit": limit},
        )

        if isinstance(response, list):
            return self._parse_list(response)
        return self._parse_list(response.get("values", response.get("data", [])))
