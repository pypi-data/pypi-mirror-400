"""
Ethos SDK Exceptions

Custom exception classes for handling API errors.
"""

from __future__ import annotations

from typing import Any


class EthosError(Exception):
    """Base exception for all Ethos SDK errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class EthosAPIError(EthosError):
    """Exception raised when the API returns an error response."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: Any | None = None,
    ) -> None:
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(message)

    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class EthosNotFoundError(EthosAPIError):
    """Exception raised when a resource is not found (404)."""

    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, status_code=404)


class EthosRateLimitError(EthosAPIError):
    """Exception raised when rate limited by the API (429)."""

    def __init__(
        self,
        message: str = "Rate limited",
        retry_after: int | None = None,
    ) -> None:
        self.retry_after = retry_after
        super().__init__(message, status_code=429)


class EthosValidationError(EthosError):
    """Exception raised when request validation fails."""

    def __init__(self, message: str, errors: list[dict[str, Any]] | None = None) -> None:
        self.errors = errors or []
        super().__init__(message)


class EthosAuthenticationError(EthosAPIError):
    """Exception raised when authentication fails (401/403)."""

    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message, status_code=401)
