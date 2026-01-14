"""
Activities resource for Ethos API.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import TYPE_CHECKING, Any

from ethos.resources.base import AsyncBaseResource, BaseResource
from ethos.types.activity import Activity

if TYPE_CHECKING:
    pass


class Activities(BaseResource[Activity]):
    """
    Activities API resource.

    Access on-chain activities (vouches, reviews, etc.).
    """

    _path = "/activities"
    _model = Activity

    def get(self, activity_id: int) -> Activity:
        """
        Get an activity by ID.

        Args:
            activity_id: The activity ID

        Returns:
            The activity
        """
        response = self._http.get(f"{self._path}/{activity_id}")
        return self._parse_item(response)

    def list(
        self,
        author_profile_id: int | None = None,
        target_profile_id: int | None = None,
        activity_type: str | None = None,
        limit: int = 100,
    ) -> Iterator[Activity]:
        """
        List activities with optional filtering.

        Args:
            author_profile_id: Filter by actor
            target_profile_id: Filter by target
            activity_type: Filter by type (vouch, review, etc.)
            limit: Page size

        Yields:
            Activity objects
        """
        params: dict[str, Any] = {}

        if author_profile_id is not None:
            params["authorProfileId"] = author_profile_id
        if target_profile_id is not None:
            params["subjectProfileId"] = target_profile_id
        if activity_type is not None:
            params["type"] = activity_type

        yield from self._paginate(self._path, params=params, limit=limit)

    def for_profile(self, profile_id: int) -> list[Activity]:
        """
        Get all activities involving a profile (as actor or target).

        Args:
            profile_id: The profile ID

        Returns:
            List of activities
        """
        # Get activities where profile is author
        as_author = list(self.list(author_profile_id=profile_id))
        # Get activities where profile is target
        as_target = list(self.list(target_profile_id=profile_id))

        # Combine and dedupe by ID
        seen = set()
        combined = []
        for activity in as_author + as_target:
            if activity.id not in seen:
                seen.add(activity.id)
                combined.append(activity)

        # Sort by created_at
        return sorted(combined, key=lambda a: a.created_at or "", reverse=True)

    def vouches(self, limit: int = 100) -> Iterator[Activity]:
        """Get vouch activities."""
        yield from self.list(activity_type="vouch", limit=limit)

    def reviews(self, limit: int = 100) -> Iterator[Activity]:
        """Get review activities."""
        yield from self.list(activity_type="review", limit=limit)

    def recent(self, limit: int = 20) -> list[Activity]:
        """
        Get recent activities.

        Args:
            limit: Number of activities

        Returns:
            Recent activities
        """
        activities = []
        for activity in self.list(limit=limit):
            activities.append(activity)
            if len(activities) >= limit:
                break
        return activities


class AsyncActivities(AsyncBaseResource[Activity]):
    """Async Activities API resource."""

    _path = "/activities"
    _model = Activity

    async def get(self, activity_id: int) -> Activity:
        """Get an activity by ID."""
        response = await self._http.get(f"{self._path}/{activity_id}")
        return self._parse_item(response)

    async def list(
        self,
        author_profile_id: int | None = None,
        target_profile_id: int | None = None,
        activity_type: str | None = None,
        limit: int = 100,
    ) -> AsyncIterator[Activity]:
        """List activities with optional filtering."""
        params: dict[str, Any] = {}

        if author_profile_id is not None:
            params["authorProfileId"] = author_profile_id
        if target_profile_id is not None:
            params["subjectProfileId"] = target_profile_id
        if activity_type is not None:
            params["type"] = activity_type

        async for activity in self._paginate(self._path, params=params, limit=limit):
            yield activity

    async def recent(self, limit: int = 20) -> list[Activity]:
        """Get recent activities."""
        activities = []
        async for activity in self.list(limit=limit):
            activities.append(activity)
            if len(activities) >= limit:
                break
        return activities
