"""
HTTP client for making API requests.
"""

from __future__ import annotations

import time
from typing import Any, TypeVar

import httpx
from pydantic import BaseModel
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from ethos._config import DEFAULT_CONFIG, EthosConfig
from ethos.exceptions import (
    EthosAPIError,
    EthosAuthenticationError,
    EthosNotFoundError,
    EthosRateLimitError,
)

T = TypeVar("T", bound=BaseModel)


class HTTPClient:
    """
    Low-level HTTP client for Ethos API.

    Handles request/response, rate limiting, retries, and error handling.
    """

    def __init__(self, config: EthosConfig | None = None) -> None:
        self.config = config or DEFAULT_CONFIG
        self._last_request_time: float = 0
        self._client: httpx.Client | None = None

    @property
    def client(self) -> httpx.Client:
        """Get or create the HTTP client."""
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.config.base_url,
                timeout=self.config.timeout,
                headers=self._default_headers(),
            )
        return self._client

    def _default_headers(self) -> dict[str, str]:
        """Get default headers for all requests."""
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Ethos-Client": self.config.client_name,
        }

    def _rate_limit(self) -> None:
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.config.rate_limit:
            time.sleep(self.config.rate_limit - elapsed)
        self._last_request_time = time.time()

    def _handle_error(self, response: httpx.Response) -> None:
        """Handle error responses from the API."""
        if response.status_code == 404:
            raise EthosNotFoundError()

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise EthosRateLimitError(retry_after=int(retry_after) if retry_after else None)

        if response.status_code in (401, 403):
            raise EthosAuthenticationError()

        if response.status_code >= 400:
            try:
                body = response.json()
                message = body.get("message", body.get("error", str(body)))
            except Exception:
                message = response.text or f"HTTP {response.status_code}"

            raise EthosAPIError(
                message=message,
                status_code=response.status_code,
                response_body=response.text,
            )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
    )
    def request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Make an HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API endpoint path
            params: Query parameters
            json: JSON body data

        Returns:
            Parsed JSON response

        Raises:
            EthosAPIError: On API errors
        """
        self._rate_limit()

        # Clean up params - remove None values
        if params:
            params = {k: v for k, v in params.items() if v is not None}

        response = self.client.request(
            method=method,
            url=path,
            params=params,
            json=json,
        )

        self._handle_error(response)

        if response.status_code == 204:
            return {}

        return response.json()

    def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make a GET request."""
        return self.request("GET", path, params=params)

    def post(
        self,
        path: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make a POST request."""
        return self.request("POST", path, params=params, json=json)

    def put(
        self,
        path: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make a PUT request."""
        return self.request("PUT", path, params=params, json=json)

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            self._client.close()
            self._client = None

    def __enter__(self) -> HTTPClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


class AsyncHTTPClient:
    """
    Async HTTP client for Ethos API.
    """

    def __init__(self, config: EthosConfig | None = None) -> None:
        self.config = config or DEFAULT_CONFIG
        self._last_request_time: float = 0
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Get or create the async HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.config.base_url,
                timeout=self.config.timeout,
                headers=self._default_headers(),
            )
        return self._client

    def _default_headers(self) -> dict[str, str]:
        """Get default headers for all requests."""
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Ethos-Client": self.config.client_name,
        }

    async def _rate_limit(self) -> None:
        """Enforce rate limiting between requests."""
        import asyncio

        elapsed = time.time() - self._last_request_time
        if elapsed < self.config.rate_limit:
            await asyncio.sleep(self.config.rate_limit - elapsed)
        self._last_request_time = time.time()

    def _handle_error(self, response: httpx.Response) -> None:
        """Handle error responses from the API."""
        if response.status_code == 404:
            raise EthosNotFoundError()

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise EthosRateLimitError(retry_after=int(retry_after) if retry_after else None)

        if response.status_code in (401, 403):
            raise EthosAuthenticationError()

        if response.status_code >= 400:
            try:
                body = response.json()
                message = body.get("message", body.get("error", str(body)))
            except Exception:
                message = response.text or f"HTTP {response.status_code}"

            raise EthosAPIError(
                message=message,
                status_code=response.status_code,
                response_body=response.text,
            )

    async def request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an async HTTP request to the API."""
        await self._rate_limit()

        if params:
            params = {k: v for k, v in params.items() if v is not None}

        response = await self.client.request(
            method=method,
            url=path,
            params=params,
            json=json,
        )

        self._handle_error(response)

        if response.status_code == 204:
            return {}

        return response.json()

    async def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an async GET request."""
        return await self.request("GET", path, params=params)

    async def post(
        self,
        path: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an async POST request."""
        return await self.request("POST", path, params=params, json=json)

    async def put(
        self,
        path: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an async PUT request."""
        return await self.request("PUT", path, params=params, json=json)

    async def close(self) -> None:
        """Close the async HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> AsyncHTTPClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
