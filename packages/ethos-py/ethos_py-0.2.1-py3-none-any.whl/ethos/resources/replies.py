"""
Replies resource for Ethos API.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import TYPE_CHECKING, Any, Literal

from ethos.resources.base import AsyncBaseResource, BaseResource
from ethos.types.reply import Reply, ReplyContractType

if TYPE_CHECKING:
    pass


class Replies(BaseResource[Reply]):
    """
    Replies API resource.

    Access replies/comments on activities.
    """

    _path = "/replies"
    _model = Reply

    def get_by_ids(self, ids: list[int]) -> list[Reply]:
        """
        Get replies by their IDs.

        Args:
            ids: List of reply IDs

        Returns:
            List of replies
        """
        response = self._http.get(f"{self._path}/by-id", params={"ids": ids})
        if isinstance(response, list):
            return self._parse_list(response)
        # Response might be a dict with reply IDs as keys
        if isinstance(response, dict):
            return [Reply.model_validate(v) for v in response.values() if v]
        return []

    def get(self, reply_id: int) -> Reply | None:
        """
        Get a single reply by ID.

        Args:
            reply_id: The reply ID

        Returns:
            The reply or None if not found
        """
        replies = self.get_by_ids([reply_id])
        return replies[0] if replies else None

    def list(
        self,
        contract_type: ReplyContractType,
        parent_id: int,
        order_by: Literal["score", "createdAt", "votes"] = "createdAt",
        order_direction: Literal["asc", "desc"] = "desc",
        limit: int = 50,
        offset: int = 0,
    ) -> Iterator[Reply]:
        """
        Get replies for an activity.

        Args:
            contract_type: Type of parent activity
            parent_id: ID of the parent activity
            order_by: Sort field
            order_direction: Sort direction
            limit: Page size
            offset: Starting offset

        Yields:
            Reply objects
        """
        params: dict[str, Any] = {
            "orderBy": order_by,
            "orderDirection": order_direction,
            "limit": limit,
            "offset": offset,
        }
        yield from self._paginate(
            f"{self._path}/{contract_type}/{parent_id}",
            params=params,
            limit=limit,
        )

    def for_review(self, review_id: int, limit: int = 50) -> list[Reply]:
        """
        Get replies for a review.

        Args:
            review_id: The review ID
            limit: Maximum replies

        Returns:
            List of replies
        """
        return list(self.list("review", review_id, limit=limit))

    def for_vouch(self, vouch_id: int, limit: int = 50) -> list[Reply]:
        """
        Get replies for a vouch.

        Args:
            vouch_id: The vouch ID
            limit: Maximum replies

        Returns:
            List of replies
        """
        return list(self.list("vouch", vouch_id, limit=limit))

    def for_project(self, project_id: int, limit: int = 50) -> list[Reply]:
        """
        Get replies for a project.

        Args:
            project_id: The project ID
            limit: Maximum replies

        Returns:
            List of replies
        """
        return list(self.list("project", project_id, limit=limit))


class AsyncReplies(AsyncBaseResource[Reply]):
    """Async Replies API resource."""

    _path = "/replies"
    _model = Reply

    async def get_by_ids(self, ids: list[int]) -> list[Reply]:
        """Get replies by their IDs."""
        response = await self._http.get(f"{self._path}/by-id", params={"ids": ids})
        if isinstance(response, list):
            return self._parse_list(response)
        if isinstance(response, dict):
            return [Reply.model_validate(v) for v in response.values() if v]
        return []

    async def get(self, reply_id: int) -> Reply | None:
        """Get a single reply by ID."""
        replies = await self.get_by_ids([reply_id])
        return replies[0] if replies else None

    async def list(
        self,
        contract_type: ReplyContractType,
        parent_id: int,
        order_by: Literal["score", "createdAt", "votes"] = "createdAt",
        order_direction: Literal["asc", "desc"] = "desc",
        limit: int = 50,
        offset: int = 0,
    ) -> AsyncIterator[Reply]:
        """Get replies for an activity."""
        params: dict[str, Any] = {
            "orderBy": order_by,
            "orderDirection": order_direction,
            "limit": limit,
            "offset": offset,
        }
        async for reply in self._paginate(
            f"{self._path}/{contract_type}/{parent_id}",
            params=params,
            limit=limit,
        ):
            yield reply

    async def for_review(self, review_id: int, limit: int = 50) -> list[Reply]:
        """Get replies for a review."""
        replies = []
        async for reply in self.list("review", review_id, limit=limit):
            replies.append(reply)
        return replies

    async def for_vouch(self, vouch_id: int, limit: int = 50) -> list[Reply]:
        """Get replies for a vouch."""
        replies = []
        async for reply in self.list("vouch", vouch_id, limit=limit):
            replies.append(reply)
        return replies

    async def for_project(self, project_id: int, limit: int = 50) -> list[Reply]:
        """Get replies for a project."""
        replies = []
        async for reply in self.list("project", project_id, limit=limit):
            replies.append(reply)
        return replies
