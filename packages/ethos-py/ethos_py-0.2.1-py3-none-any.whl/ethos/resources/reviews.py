"""
Reviews resource for Ethos API.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import TYPE_CHECKING, Any, Literal

from ethos.resources.base import AsyncBaseResource, BaseResource
from ethos.types.review import Review

if TYPE_CHECKING:
    pass


ReviewScore = Literal["positive", "neutral", "negative"]


class Reviews(BaseResource[Review]):
    """
    Reviews API resource.

    Access reviews left between profiles.
    """

    _path = "/reviews"
    _model = Review

    def get(self, review_id: int) -> Review:
        """
        Get a review by ID.

        Args:
            review_id: The review ID

        Returns:
            The review
        """
        response = self._http.get(f"{self._path}/{review_id}")
        return self._parse_item(response)

    def list(
        self,
        author_profile_id: int | None = None,
        target_profile_id: int | None = None,
        score: ReviewScore | None = None,
        archived: bool | None = None,
        limit: int = 100,
    ) -> Iterator[Review]:
        """
        List reviews with optional filtering.

        Args:
            author_profile_id: Filter by reviewer
            target_profile_id: Filter by review target
            score: Filter by sentiment (positive/neutral/negative)
            archived: Filter by archived status
            limit: Page size

        Yields:
            Review objects
        """
        params: dict[str, Any] = {}

        if author_profile_id is not None:
            params["authorProfileId"] = author_profile_id
        if target_profile_id is not None:
            params["subjectProfileId"] = target_profile_id
        if score is not None:
            params["score"] = score
        if archived is not None:
            params["archived"] = archived

        yield from self._paginate(self._path, params=params, limit=limit)

    def for_profile(self, profile_id: int) -> list[Review]:
        """
        Get all reviews received by a profile.

        Args:
            profile_id: The profile ID

        Returns:
            List of reviews received
        """
        return list(self.list(target_profile_id=profile_id))

    def by_profile(self, profile_id: int) -> list[Review]:
        """
        Get all reviews given by a profile.

        Args:
            profile_id: The profile ID

        Returns:
            List of reviews given
        """
        return list(self.list(author_profile_id=profile_id))

    def positive_for(self, profile_id: int) -> list[Review]:
        """Get positive reviews received by a profile."""
        return list(self.list(target_profile_id=profile_id, score="positive"))

    def negative_for(self, profile_id: int) -> list[Review]:
        """Get negative reviews received by a profile."""
        return list(self.list(target_profile_id=profile_id, score="negative"))


class AsyncReviews(AsyncBaseResource[Review]):
    """Async Reviews API resource."""

    _path = "/reviews"
    _model = Review

    async def get(self, review_id: int) -> Review:
        """Get a review by ID."""
        response = await self._http.get(f"{self._path}/{review_id}")
        return self._parse_item(response)

    async def list(
        self,
        author_profile_id: int | None = None,
        target_profile_id: int | None = None,
        score: ReviewScore | None = None,
        archived: bool | None = None,
        limit: int = 100,
    ) -> AsyncIterator[Review]:
        """List reviews with optional filtering."""
        params: dict[str, Any] = {}

        if author_profile_id is not None:
            params["authorProfileId"] = author_profile_id
        if target_profile_id is not None:
            params["subjectProfileId"] = target_profile_id
        if score is not None:
            params["score"] = score
        if archived is not None:
            params["archived"] = archived

        async for review in self._paginate(self._path, params=params, limit=limit):
            yield review

    async def for_profile(self, profile_id: int) -> list[Review]:
        """Get all reviews received by a profile."""
        reviews = []
        async for review in self.list(target_profile_id=profile_id):
            reviews.append(review)
        return reviews

    async def by_profile(self, profile_id: int) -> list[Review]:
        """Get all reviews given by a profile."""
        reviews = []
        async for review in self.list(author_profile_id=profile_id):
            reviews.append(review)
        return reviews
