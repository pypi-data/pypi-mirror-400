from __future__ import annotations

import os
from typing import Any

import httpx

from mcsrranked._constants import BASE_URL, DEFAULT_MAX_RETRIES, DEFAULT_TIMEOUT
from mcsrranked._exceptions import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    NotFoundError,
    RateLimitError,
)

__all__ = ["SyncAPIClient", "AsyncAPIClient"]


class BaseAPIClient:
    """Base class for sync and async API clients."""

    _base_url: str
    _api_key: str | None
    _private_key: str | None
    _timeout: float
    _max_retries: int

    def __init__(
        self,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
        private_key: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
    ) -> None:
        self._base_url = base_url or BASE_URL
        self._api_key = api_key or os.environ.get("MCSRRANKED_API_KEY")
        self._private_key = private_key or os.environ.get("MCSRRANKED_PRIVATE_KEY")
        self._timeout = timeout if timeout is not None else DEFAULT_TIMEOUT
        self._max_retries = (
            max_retries if max_retries is not None else DEFAULT_MAX_RETRIES
        )

    def _build_headers(self, *, require_private_key: bool = False) -> dict[str, str]:
        """Build request headers."""
        headers: dict[str, str] = {
            "Accept": "application/json",
            "User-Agent": "mcsrranked-python/0.1.0",
        }
        if self._api_key:
            headers["API-Key"] = self._api_key
        if require_private_key:
            if not self._private_key:
                raise AuthenticationError(
                    "Private key is required for this endpoint. "
                    "Set it via MCSRRanked(private_key=...) or MCSRRANKED_PRIVATE_KEY env var.",
                    status_code=401,
                    response=httpx.Response(401),
                    body=None,
                )
            headers["Private-Key"] = self._private_key
        return headers

    def _build_request_params(
        self, params: dict[str, Any] | None
    ) -> dict[str, Any] | None:
        """Filter out None values from params."""
        if params is None:
            return None
        return {k: v for k, v in params.items() if v is not None}

    def _make_status_error(
        self,
        response: httpx.Response,
        body: object | None = None,
    ) -> APIStatusError:
        """Create appropriate exception based on status code."""
        message = f"API request failed with status {response.status_code}"
        if isinstance(body, dict) and "data" in body:
            message = f"{message}: {body['data']}"

        error_class: type[APIStatusError]
        if response.status_code == 400:
            error_class = BadRequestError
        elif response.status_code == 401:
            error_class = AuthenticationError
        elif response.status_code == 404:
            error_class = NotFoundError
        elif response.status_code == 429:
            error_class = RateLimitError
        else:
            error_class = APIStatusError

        return error_class(
            message,
            status_code=response.status_code,
            response=response,
            body=body,
        )

    def _process_response(self, response: httpx.Response) -> dict[str, Any]:
        """Process response and handle errors."""
        try:
            body = response.json()
        except Exception:
            body = None

        if response.status_code >= 400:
            raise self._make_status_error(response, body)

        if not isinstance(body, dict):
            raise APIConnectionError(f"Unexpected response format: {type(body)}")

        return body


class SyncAPIClient(BaseAPIClient):
    """Synchronous HTTP client for the MCSR Ranked API."""

    _client: httpx.Client | None

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._client = None

    @property
    def client(self) -> httpx.Client:
        """Get or create the httpx client."""
        if self._client is None:
            self._client = httpx.Client(
                base_url=self._base_url,
                timeout=self._timeout,
            )
        return self._client

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        require_private_key: bool = False,
    ) -> dict[str, Any]:
        """Make an HTTP request."""
        headers = self._build_headers(require_private_key=require_private_key)
        filtered_params = self._build_request_params(params)

        try:
            response = self.client.request(
                method,
                path,
                params=filtered_params,
                headers=headers,
            )
        except httpx.TimeoutException as e:
            raise APITimeoutError(f"Request timed out: {e}") from e
        except httpx.RequestError as e:
            raise APIConnectionError(f"Connection error: {e}") from e

        return self._process_response(response)

    def get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        require_private_key: bool = False,
    ) -> dict[str, Any]:
        """Make a GET request."""
        return self.request(
            "GET", path, params=params, require_private_key=require_private_key
        )

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            self._client.close()
            self._client = None

    def __enter__(self) -> SyncAPIClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


class AsyncAPIClient(BaseAPIClient):
    """Asynchronous HTTP client for the MCSR Ranked API."""

    _client: httpx.AsyncClient | None

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Get or create the httpx async client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                timeout=self._timeout,
            )
        return self._client

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        require_private_key: bool = False,
    ) -> dict[str, Any]:
        """Make an async HTTP request."""
        headers = self._build_headers(require_private_key=require_private_key)
        filtered_params = self._build_request_params(params)

        try:
            response = await self.client.request(
                method,
                path,
                params=filtered_params,
                headers=headers,
            )
        except httpx.TimeoutException as e:
            raise APITimeoutError(f"Request timed out: {e}") from e
        except httpx.RequestError as e:
            raise APIConnectionError(f"Connection error: {e}") from e

        return self._process_response(response)

    async def get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        require_private_key: bool = False,
    ) -> dict[str, Any]:
        """Make an async GET request."""
        return await self.request(
            "GET", path, params=params, require_private_key=require_private_key
        )

    async def close(self) -> None:
        """Close the async HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> AsyncAPIClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
