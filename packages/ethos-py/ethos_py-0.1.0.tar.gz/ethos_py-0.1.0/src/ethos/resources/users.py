"""
Users resource for Ethos API.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ethos.resources.base import AsyncBaseResource, BaseResource
from ethos.types.user import CategoryRank, User

if TYPE_CHECKING:
    pass


class Users(BaseResource[User]):
    """
    Users API resource.

    Access Ethos users by various identifiers (ID, address, username, social accounts).
    """

    _path = "/user"
    _model = User

    def get(self, user_id: int) -> User:
        """
        Get a user by ID.

        Args:
            user_id: The Ethos user ID

        Returns:
            The user
        """
        response = self._http.get(f"{self._path}/{user_id}")
        return self._parse_item(response)

    def get_by_address(self, address: str) -> User:
        """
        Get a user by Ethereum address.

        Args:
            address: The Ethereum address (0x...)

        Returns:
            The user
        """
        response = self._http.get(f"{self._path}/by/address/{address}")
        return self._parse_item(response)

    def get_by_profile_id(self, profile_id: int) -> User:
        """
        Get a user by profile ID.

        Args:
            profile_id: The profile ID

        Returns:
            The user
        """
        response = self._http.get(f"{self._path}/by/profile-id/{profile_id}")
        return self._parse_item(response)

    def get_by_username(self, username: str) -> User:
        """
        Get a user by username.

        Args:
            username: The Ethos username

        Returns:
            The user
        """
        response = self._http.get(f"{self._path}/by/username/{username}")
        return self._parse_item(response)

    def get_by_twitter(self, handle: str) -> User:
        """
        Get a user by Twitter/X handle or account ID.

        Args:
            handle: Twitter username or account ID

        Returns:
            The user
        """
        handle = handle.lstrip("@")
        response = self._http.get(f"{self._path}/by/x/{handle}")
        return self._parse_item(response)

    def get_by_discord(self, discord_id: str) -> User:
        """
        Get a user by Discord ID.

        Args:
            discord_id: The Discord user ID

        Returns:
            The user
        """
        response = self._http.get(f"{self._path}/by/discord/{discord_id}")
        return self._parse_item(response)

    def get_by_farcaster(self, farcaster_id: str) -> User:
        """
        Get a user by Farcaster ID.

        Args:
            farcaster_id: The Farcaster user ID

        Returns:
            The user
        """
        response = self._http.get(f"{self._path}/by/farcaster/{farcaster_id}")
        return self._parse_item(response)

    def get_by_farcaster_username(self, username: str) -> User:
        """
        Get a user by Farcaster username.

        Args:
            username: The Farcaster username

        Returns:
            The user
        """
        response = self._http.get(f"{self._path}/by/farcaster/username/{username}")
        return self._parse_item(response)

    def get_by_telegram(self, telegram_id: str) -> User:
        """
        Get a user by Telegram ID.

        Args:
            telegram_id: The Telegram user ID

        Returns:
            The user
        """
        response = self._http.get(f"{self._path}/by/telegram/{telegram_id}")
        return self._parse_item(response)

    def search(
        self,
        query: str,
        user_key_type: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[User]:
        """
        Search for users.

        Args:
            query: Search query (2-100 characters)
            user_key_type: Optional filter by userkey type
            limit: Maximum results
            offset: Pagination offset

        Returns:
            List of matching users
        """
        params: dict[str, Any] = {
            "query": query,
            "limit": limit,
            "offset": offset,
        }
        if user_key_type:
            params["userKeyType"] = user_key_type

        response = self._http.get("/users/search", params=params)
        if isinstance(response, list):
            return self._parse_list(response)
        return self._parse_list(response.get("values", []))

    def bulk_by_ids(self, user_ids: list[int]) -> list[User]:
        """
        Get multiple users by their IDs.

        Args:
            user_ids: List of user IDs (1-500)

        Returns:
            List of users
        """
        response = self._http.post("/users/by/ids", json={"userIds": user_ids})
        if isinstance(response, list):
            return self._parse_list(response)
        return self._parse_list(response.get("values", response.get("data", [])))

    def bulk_by_addresses(self, addresses: list[str]) -> list[User]:
        """
        Get multiple users by addresses.

        Args:
            addresses: List of Ethereum addresses (1-500)

        Returns:
            List of users
        """
        response = self._http.post("/users/by/address", json={"addresses": addresses})
        if isinstance(response, list):
            return self._parse_list(response)
        return self._parse_list(response.get("values", response.get("data", [])))

    def bulk_by_profile_ids(self, profile_ids: list[int]) -> list[User]:
        """
        Get multiple users by profile IDs.

        Args:
            profile_ids: List of profile IDs (1-500)

        Returns:
            List of users
        """
        response = self._http.post("/users/by/profile-id", json={"profileIds": profile_ids})
        if isinstance(response, list):
            return self._parse_list(response)
        return self._parse_list(response.get("values", response.get("data", [])))

    def bulk_by_twitter(self, handles: list[str]) -> list[User]:
        """
        Get multiple users by Twitter handles.

        Args:
            handles: List of Twitter handles (1-500)

        Returns:
            List of users
        """
        response = self._http.post("/users/by/x", json={"accountIdsOrUsernames": handles})
        if isinstance(response, list):
            return self._parse_list(response)
        return self._parse_list(response.get("values", response.get("data", [])))

    def get_categories(self, userkey: str) -> list[CategoryRank]:
        """
        Get a user's category rankings.

        Args:
            userkey: The user's userkey

        Returns:
            List of category ranks
        """
        response = self._http.get(f"/users/{userkey}/categories")
        ranks = response.get("categoryRanks", [])
        return [CategoryRank.model_validate(r) for r in ranks]


class AsyncUsers(AsyncBaseResource[User]):
    """Async Users API resource."""

    _path = "/user"
    _model = User

    async def get(self, user_id: int) -> User:
        """Get a user by ID."""
        response = await self._http.get(f"{self._path}/{user_id}")
        return self._parse_item(response)

    async def get_by_address(self, address: str) -> User:
        """Get a user by Ethereum address."""
        response = await self._http.get(f"{self._path}/by/address/{address}")
        return self._parse_item(response)

    async def get_by_profile_id(self, profile_id: int) -> User:
        """Get a user by profile ID."""
        response = await self._http.get(f"{self._path}/by/profile-id/{profile_id}")
        return self._parse_item(response)

    async def get_by_username(self, username: str) -> User:
        """Get a user by username."""
        response = await self._http.get(f"{self._path}/by/username/{username}")
        return self._parse_item(response)

    async def get_by_twitter(self, handle: str) -> User:
        """Get a user by Twitter/X handle."""
        handle = handle.lstrip("@")
        response = await self._http.get(f"{self._path}/by/x/{handle}")
        return self._parse_item(response)

    async def get_by_discord(self, discord_id: str) -> User:
        """Get a user by Discord ID."""
        response = await self._http.get(f"{self._path}/by/discord/{discord_id}")
        return self._parse_item(response)

    async def get_by_farcaster(self, farcaster_id: str) -> User:
        """Get a user by Farcaster ID."""
        response = await self._http.get(f"{self._path}/by/farcaster/{farcaster_id}")
        return self._parse_item(response)

    async def get_by_farcaster_username(self, username: str) -> User:
        """Get a user by Farcaster username."""
        response = await self._http.get(f"{self._path}/by/farcaster/username/{username}")
        return self._parse_item(response)

    async def get_by_telegram(self, telegram_id: str) -> User:
        """Get a user by Telegram ID."""
        response = await self._http.get(f"{self._path}/by/telegram/{telegram_id}")
        return self._parse_item(response)

    async def search(
        self,
        query: str,
        user_key_type: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[User]:
        """Search for users."""
        params: dict[str, Any] = {
            "query": query,
            "limit": limit,
            "offset": offset,
        }
        if user_key_type:
            params["userKeyType"] = user_key_type

        response = await self._http.get("/users/search", params=params)
        if isinstance(response, list):
            return self._parse_list(response)
        return self._parse_list(response.get("values", []))

    async def bulk_by_ids(self, user_ids: list[int]) -> list[User]:
        """Get multiple users by their IDs."""
        response = await self._http.post("/users/by/ids", json={"userIds": user_ids})
        if isinstance(response, list):
            return self._parse_list(response)
        return self._parse_list(response.get("values", response.get("data", [])))

    async def bulk_by_addresses(self, addresses: list[str]) -> list[User]:
        """Get multiple users by addresses."""
        response = await self._http.post("/users/by/address", json={"addresses": addresses})
        if isinstance(response, list):
            return self._parse_list(response)
        return self._parse_list(response.get("values", response.get("data", [])))

    async def bulk_by_profile_ids(self, profile_ids: list[int]) -> list[User]:
        """Get multiple users by profile IDs."""
        response = await self._http.post("/users/by/profile-id", json={"profileIds": profile_ids})
        if isinstance(response, list):
            return self._parse_list(response)
        return self._parse_list(response.get("values", response.get("data", [])))

    async def bulk_by_twitter(self, handles: list[str]) -> list[User]:
        """Get multiple users by Twitter handles."""
        response = await self._http.post("/users/by/x", json={"accountIdsOrUsernames": handles})
        if isinstance(response, list):
            return self._parse_list(response)
        return self._parse_list(response.get("values", response.get("data", [])))

    async def get_categories(self, userkey: str) -> list[CategoryRank]:
        """Get a user's category rankings."""
        response = await self._http.get(f"/users/{userkey}/categories")
        ranks = response.get("categoryRanks", [])
        return [CategoryRank.model_validate(r) for r in ranks]
