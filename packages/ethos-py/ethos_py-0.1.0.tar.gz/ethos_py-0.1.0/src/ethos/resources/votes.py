"""
Votes resource for Ethos API.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import TYPE_CHECKING, Any, Literal

from ethos.resources.base import AsyncBaseResource, BaseResource
from ethos.types.vote import Vote, VoteStats, VoteTargetType

if TYPE_CHECKING:
    pass


class Votes(BaseResource[Vote]):
    """
    Votes API resource.

    Access votes (upvotes/downvotes) on various activities.
    """

    _path = "/votes"
    _model = Vote

    def list(
        self,
        target_type: VoteTargetType,
        activity_id: int,
        is_upvote: bool | None = None,
        order_by: Literal["score", "updatedAt"] = "updatedAt",
        order_direction: Literal["asc", "desc"] = "desc",
        limit: int = 50,
        offset: int = 0,
    ) -> Iterator[Vote]:
        """
        Get votes for an activity.

        Args:
            target_type: Type of activity
            activity_id: ID of the activity
            is_upvote: Filter by upvote/downvote
            order_by: Sort field
            order_direction: Sort direction
            limit: Page size
            offset: Starting offset

        Yields:
            Vote objects
        """
        params: dict[str, Any] = {
            "type": target_type,
            "activityId": activity_id,
            "orderBy": order_by,
            "orderDirection": order_direction,
            "limit": limit,
            "offset": offset,
        }
        if is_upvote is not None:
            params["isUpvote"] = str(is_upvote).lower()

        yield from self._paginate(self._path, params=params, limit=limit)

    def get_stats(
        self,
        target_type: VoteTargetType,
        activity_id: int,
        include_archived: bool = False,
    ) -> VoteStats:
        """
        Get vote statistics for an activity.

        Args:
            target_type: Type of activity
            activity_id: ID of the activity
            include_archived: Include archived votes

        Returns:
            Vote statistics
        """
        response = self._http.get(
            f"{self._path}/stats",
            params={
                "type": target_type,
                "activityId": activity_id,
                "includeArchived": include_archived,
            },
        )
        return VoteStats.model_validate(response)

    def get_bulk_stats(
        self,
        review_ids: list[int] | None = None,
        vouch_ids: list[int] | None = None,
        project_ids: list[int] | None = None,
        include_archived: bool = False,
    ) -> dict[str, dict[int, VoteStats]]:
        """
        Get vote statistics for multiple activities.

        Args:
            review_ids: List of review IDs
            vouch_ids: List of vouch IDs
            project_ids: List of project IDs
            include_archived: Include archived votes

        Returns:
            Dictionary of stats by activity type and ID
        """
        body: dict[str, Any] = {"includeArchived": include_archived}
        if review_ids:
            body["review"] = review_ids
        if vouch_ids:
            body["vouch"] = vouch_ids
        if project_ids:
            body["project"] = project_ids

        response = self._http.post(f"{self._path}/stats", json=body)

        result: dict[str, dict[int, VoteStats]] = {}
        for activity_type, stats_dict in response.items():
            if isinstance(stats_dict, dict):
                result[activity_type] = {
                    int(k): VoteStats.model_validate(v) for k, v in stats_dict.items()
                }
        return result

    def upvotes_for(self, target_type: VoteTargetType, activity_id: int) -> Iterator[Vote]:
        """Get upvotes for an activity."""
        yield from self.list(target_type, activity_id, is_upvote=True)

    def downvotes_for(self, target_type: VoteTargetType, activity_id: int) -> Iterator[Vote]:
        """Get downvotes for an activity."""
        yield from self.list(target_type, activity_id, is_upvote=False)


class AsyncVotes(AsyncBaseResource[Vote]):
    """Async Votes API resource."""

    _path = "/votes"
    _model = Vote

    async def list(
        self,
        target_type: VoteTargetType,
        activity_id: int,
        is_upvote: bool | None = None,
        order_by: Literal["score", "updatedAt"] = "updatedAt",
        order_direction: Literal["asc", "desc"] = "desc",
        limit: int = 50,
        offset: int = 0,
    ) -> AsyncIterator[Vote]:
        """Get votes for an activity."""
        params: dict[str, Any] = {
            "type": target_type,
            "activityId": activity_id,
            "orderBy": order_by,
            "orderDirection": order_direction,
            "limit": limit,
            "offset": offset,
        }
        if is_upvote is not None:
            params["isUpvote"] = str(is_upvote).lower()

        async for vote in self._paginate(self._path, params=params, limit=limit):
            yield vote

    async def get_stats(
        self,
        target_type: VoteTargetType,
        activity_id: int,
        include_archived: bool = False,
    ) -> VoteStats:
        """Get vote statistics for an activity."""
        response = await self._http.get(
            f"{self._path}/stats",
            params={
                "type": target_type,
                "activityId": activity_id,
                "includeArchived": include_archived,
            },
        )
        return VoteStats.model_validate(response)

    async def get_bulk_stats(
        self,
        review_ids: list[int] | None = None,
        vouch_ids: list[int] | None = None,
        project_ids: list[int] | None = None,
        include_archived: bool = False,
    ) -> dict[str, dict[int, VoteStats]]:
        """Get vote statistics for multiple activities."""
        body: dict[str, Any] = {"includeArchived": include_archived}
        if review_ids:
            body["review"] = review_ids
        if vouch_ids:
            body["vouch"] = vouch_ids
        if project_ids:
            body["project"] = project_ids

        response = await self._http.post(f"{self._path}/stats", json=body)

        result: dict[str, dict[int, VoteStats]] = {}
        for activity_type, stats_dict in response.items():
            if isinstance(stats_dict, dict):
                result[activity_type] = {
                    int(k): VoteStats.model_validate(v) for k, v in stats_dict.items()
                }
        return result
