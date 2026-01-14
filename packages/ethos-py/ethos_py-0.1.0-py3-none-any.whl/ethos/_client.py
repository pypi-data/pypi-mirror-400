"""
Main Ethos client classes.
"""

from __future__ import annotations

from typing import Any

from ethos._config import DEFAULT_CONFIG, EthosConfig
from ethos._http import AsyncHTTPClient, HTTPClient
from ethos.resources import (
    XP,
    Activities,
    AsyncActivities,
    AsyncContributions,
    AsyncEndorsements,
    AsyncInvitations,
    AsyncMarkets,
    AsyncNotifications,
    AsyncProfiles,
    AsyncReplies,
    AsyncReviews,
    AsyncScores,
    AsyncUsers,
    AsyncVotes,
    AsyncVouches,
    AsyncXP,
    Contributions,
    Endorsements,
    Invitations,
    Markets,
    Notifications,
    Profiles,
    Replies,
    Reviews,
    Scores,
    Users,
    Votes,
    Vouches,
)


class Ethos:
    """
    Synchronous Ethos Network API client.

    Example:
        >>> from ethos import Ethos
        >>> client = Ethos()
        >>> profile = client.profiles.get_by_twitter("vitalikbuterin")
        >>> print(profile.credibility_score)
    """

    def __init__(
        self,
        client_name: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
        rate_limit: float | None = None,
        max_retries: int | None = None,
    ) -> None:
        """
        Initialize the Ethos client.

        Args:
            client_name: Name identifying your application to Ethos
            base_url: Custom API base URL
            timeout: Request timeout in seconds
            rate_limit: Minimum seconds between requests
            max_retries: Number of retries for failed requests
        """
        # Build config from defaults + overrides
        config = EthosConfig(
            base_url=base_url or DEFAULT_CONFIG.base_url,
            client_name=client_name or DEFAULT_CONFIG.client_name,
            timeout=timeout or DEFAULT_CONFIG.timeout,
            rate_limit=rate_limit or DEFAULT_CONFIG.rate_limit,
            max_retries=max_retries or DEFAULT_CONFIG.max_retries,
        )

        self._config = config
        self._http = HTTPClient(config)

        # Core resources
        self.profiles = Profiles(self._http)
        self.vouches = Vouches(self._http)
        self.reviews = Reviews(self._http)
        self.markets = Markets(self._http)
        self.activities = Activities(self._http)
        self.scores = Scores(self._http)

        # Extended resources
        self.users = Users(self._http)
        self.endorsements = Endorsements(self._http)
        self.votes = Votes(self._http)
        self.replies = Replies(self._http)
        self.xp = XP(self._http)
        self.invitations = Invitations(self._http)
        self.notifications = Notifications(self._http)
        self.contributions = Contributions(self._http)

    @property
    def config(self) -> EthosConfig:
        """Get the client configuration."""
        return self._config

    def close(self) -> None:
        """Close the HTTP client and release resources."""
        self._http.close()

    def __enter__(self) -> Ethos:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"Ethos(client_name={self._config.client_name!r})"


class AsyncEthos:
    """
    Asynchronous Ethos Network API client.

    Example:
        >>> import asyncio
        >>> from ethos import AsyncEthos
        >>>
        >>> async def main():
        ...     async with AsyncEthos() as client:
        ...         profile = await client.profiles.get_by_twitter("vitalikbuterin")
        ...         print(profile.credibility_score)
        >>>
        >>> asyncio.run(main())
    """

    def __init__(
        self,
        client_name: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
        rate_limit: float | None = None,
        max_retries: int | None = None,
    ) -> None:
        """
        Initialize the async Ethos client.

        Args:
            client_name: Name identifying your application to Ethos
            base_url: Custom API base URL
            timeout: Request timeout in seconds
            rate_limit: Minimum seconds between requests
            max_retries: Number of retries for failed requests
        """
        config = EthosConfig(
            base_url=base_url or DEFAULT_CONFIG.base_url,
            client_name=client_name or DEFAULT_CONFIG.client_name,
            timeout=timeout or DEFAULT_CONFIG.timeout,
            rate_limit=rate_limit or DEFAULT_CONFIG.rate_limit,
            max_retries=max_retries or DEFAULT_CONFIG.max_retries,
        )

        self._config = config
        self._http = AsyncHTTPClient(config)

        # Core async resources
        self.profiles = AsyncProfiles(self._http)
        self.vouches = AsyncVouches(self._http)
        self.reviews = AsyncReviews(self._http)
        self.markets = AsyncMarkets(self._http)
        self.activities = AsyncActivities(self._http)
        self.scores = AsyncScores(self._http)

        # Extended async resources
        self.users = AsyncUsers(self._http)
        self.endorsements = AsyncEndorsements(self._http)
        self.votes = AsyncVotes(self._http)
        self.replies = AsyncReplies(self._http)
        self.xp = AsyncXP(self._http)
        self.invitations = AsyncInvitations(self._http)
        self.notifications = AsyncNotifications(self._http)
        self.contributions = AsyncContributions(self._http)

    @property
    def config(self) -> EthosConfig:
        """Get the client configuration."""
        return self._config

    async def close(self) -> None:
        """Close the HTTP client and release resources."""
        await self._http.close()

    async def __aenter__(self) -> AsyncEthos:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    def __repr__(self) -> str:
        return f"AsyncEthos(client_name={self._config.client_name!r})"
