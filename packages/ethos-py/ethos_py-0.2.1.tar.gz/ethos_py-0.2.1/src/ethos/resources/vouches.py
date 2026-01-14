"""
Vouches resource for Ethos API.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import TYPE_CHECKING, Any

from ethos.resources.base import AsyncBaseResource, BaseResource
from ethos.types.vouch import Vouch

if TYPE_CHECKING:
    pass


class Vouches(BaseResource[Vouch]):
    """
    Vouches API resource.

    Access vouch relationships between profiles.
    """

    _path = "/vouches"
    _model = Vouch

    def get(self, vouch_id: int) -> Vouch:
        """
        Get a vouch by ID.

        Args:
            vouch_id: The vouch ID

        Returns:
            The vouch
        """
        response = self._http.get(f"{self._path}/{vouch_id}")
        return self._parse_item(response)

    def list(
        self,
        author_profile_id: int | None = None,
        target_profile_id: int | None = None,
        staked: bool | None = None,
        archived: bool | None = None,
        limit: int = 100,
    ) -> Iterator[Vouch]:
        """
        List vouches with optional filtering.

        Args:
            author_profile_id: Filter by voucher (who gave the vouch)
            target_profile_id: Filter by target (who received the vouch)
            staked: Filter by staked status
            archived: Filter by archived status
            limit: Page size

        Yields:
            Vouch objects
        """
        params: dict[str, Any] = {}

        if author_profile_id is not None:
            params["authorProfileId"] = author_profile_id
        if target_profile_id is not None:
            params["subjectProfileId"] = target_profile_id
        if staked is not None:
            params["staked"] = staked
        if archived is not None:
            params["archived"] = archived

        yield from self._paginate(self._path, params=params, limit=limit)

    def for_profile(self, profile_id: int) -> list[Vouch]:
        """
        Get all vouches received by a profile.

        Args:
            profile_id: The profile ID

        Returns:
            List of vouches received
        """
        return list(self.list(target_profile_id=profile_id))

    def by_profile(self, profile_id: int) -> list[Vouch]:
        """
        Get all vouches given by a profile.

        Args:
            profile_id: The profile ID

        Returns:
            List of vouches given
        """
        return list(self.list(author_profile_id=profile_id))

    def between(self, voucher_id: int, target_id: int) -> Vouch | None:
        """
        Get the vouch between two profiles if it exists.

        Args:
            voucher_id: Profile who gave the vouch
            target_id: Profile who received the vouch

        Returns:
            The vouch if it exists, None otherwise
        """
        vouches = list(
            self.list(
                author_profile_id=voucher_id,
                target_profile_id=target_id,
                limit=1,
            )
        )
        return vouches[0] if vouches else None


class AsyncVouches(AsyncBaseResource[Vouch]):
    """Async Vouches API resource."""

    _path = "/vouches"
    _model = Vouch

    async def get(self, vouch_id: int) -> Vouch:
        """Get a vouch by ID."""
        response = await self._http.get(f"{self._path}/{vouch_id}")
        return self._parse_item(response)

    async def list(
        self,
        author_profile_id: int | None = None,
        target_profile_id: int | None = None,
        staked: bool | None = None,
        archived: bool | None = None,
        limit: int = 100,
    ) -> AsyncIterator[Vouch]:
        """List vouches with optional filtering."""
        params: dict[str, Any] = {}

        if author_profile_id is not None:
            params["authorProfileId"] = author_profile_id
        if target_profile_id is not None:
            params["subjectProfileId"] = target_profile_id
        if staked is not None:
            params["staked"] = staked
        if archived is not None:
            params["archived"] = archived

        async for vouch in self._paginate(self._path, params=params, limit=limit):
            yield vouch

    async def for_profile(self, profile_id: int) -> list[Vouch]:
        """Get all vouches received by a profile."""
        vouches = []
        async for vouch in self.list(target_profile_id=profile_id):
            vouches.append(vouch)
        return vouches

    async def by_profile(self, profile_id: int) -> list[Vouch]:
        """Get all vouches given by a profile."""
        vouches = []
        async for vouch in self.list(author_profile_id=profile_id):
            vouches.append(vouch)
        return vouches

    async def between(self, voucher_id: int, target_id: int) -> Vouch | None:
        """Get the vouch between two profiles if it exists."""
        async for vouch in self.list(
            author_profile_id=voucher_id,
            target_profile_id=target_id,
            limit=1,
        ):
            return vouch
        return None
