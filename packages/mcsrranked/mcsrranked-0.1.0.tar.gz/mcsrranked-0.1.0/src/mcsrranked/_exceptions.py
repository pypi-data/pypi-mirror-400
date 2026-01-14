from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import httpx

__all__ = [
    "MCSRRankedError",
    "APIError",
    "APIStatusError",
    "BadRequestError",
    "AuthenticationError",
    "NotFoundError",
    "RateLimitError",
    "APIConnectionError",
    "APITimeoutError",
]


class MCSRRankedError(Exception):
    """Base exception for all MCSR Ranked SDK errors."""


class APIError(MCSRRankedError):
    """Base exception for API-related errors."""

    message: str

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class APIStatusError(APIError):
    """Exception raised when the API returns an error status code."""

    status_code: int
    response: httpx.Response
    body: object | None

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        response: httpx.Response,
        body: object | None = None,
    ) -> None:
        self.status_code = status_code
        self.response = response
        self.body = body
        super().__init__(message)


class BadRequestError(APIStatusError):
    """Exception raised for 400 Bad Request responses."""


class AuthenticationError(APIStatusError):
    """Exception raised for 401 Unauthorized responses."""


class NotFoundError(APIStatusError):
    """Exception raised for 404 Not Found responses."""


class RateLimitError(APIStatusError):
    """Exception raised for 429 Too Many Requests responses."""


class APIConnectionError(APIError):
    """Exception raised when a connection error occurs."""


class APITimeoutError(APIConnectionError):
    """Exception raised when a request times out."""
