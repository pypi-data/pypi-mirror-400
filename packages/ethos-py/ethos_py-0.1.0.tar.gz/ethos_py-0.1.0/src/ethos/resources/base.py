"""
Base resource class for API endpoints.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from pydantic import BaseModel

if TYPE_CHECKING:
    from ethos._http import AsyncHTTPClient, HTTPClient

T = TypeVar("T", bound=BaseModel)


class BaseResource(Generic[T]):
    """
    Base class for sync API resources.

    Provides common functionality for pagination, model parsing, etc.
    """

    _path: str = ""
    _model: type[T]

    def __init__(self, http: HTTPClient) -> None:
        self._http = http

    def _parse_item(self, data: dict[str, Any]) -> T:
        """Parse a single item from API response."""
        return self._model.model_validate(data)

    def _parse_list(self, data: list[dict[str, Any]]) -> list[T]:
        """Parse a list of items from API response."""
        return [self._parse_item(item) for item in data]

    def _paginate(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        limit: int = 100,
    ) -> Iterator[T]:
        """
        Iterate through all pages of results.

        Yields individual items, automatically fetching new pages as needed.
        """
        params = params or {}
        offset = 0

        while True:
            params["limit"] = limit
            params["offset"] = offset

            response = self._http.get(path, params=params)

            # Handle different response formats
            if isinstance(response, list):
                items = response
            elif "data" in response:
                items = response["data"]
            elif "values" in response:
                items = response["values"]
            else:
                items = response.get("results", [])

            if not items:
                break

            for item in items:
                yield self._parse_item(item)

            # Check if we've fetched all items
            if len(items) < limit:
                break

            offset += limit


class AsyncBaseResource(Generic[T]):
    """
    Base class for async API resources.
    """

    _path: str = ""
    _model: type[T]

    def __init__(self, http: AsyncHTTPClient) -> None:
        self._http = http

    def _parse_item(self, data: dict[str, Any]) -> T:
        """Parse a single item from API response."""
        return self._model.model_validate(data)

    def _parse_list(self, data: list[dict[str, Any]]) -> list[T]:
        """Parse a list of items from API response."""
        return [self._parse_item(item) for item in data]

    async def _paginate(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        limit: int = 100,
    ) -> AsyncIterator[T]:
        """
        Async iterate through all pages of results.
        """
        params = params or {}
        offset = 0

        while True:
            params["limit"] = limit
            params["offset"] = offset

            response = await self._http.get(path, params=params)

            if isinstance(response, list):
                items = response
            elif "data" in response:
                items = response["data"]
            elif "values" in response:
                items = response["values"]
            else:
                items = response.get("results", [])

            if not items:
                break

            for item in items:
                yield self._parse_item(item)

            if len(items) < limit:
                break

            offset += limit
