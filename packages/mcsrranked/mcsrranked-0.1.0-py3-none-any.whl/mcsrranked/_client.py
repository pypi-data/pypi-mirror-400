from __future__ import annotations

from functools import cached_property
from typing import Any

from mcsrranked._base_client import AsyncAPIClient, SyncAPIClient
from mcsrranked._constants import BASE_URL, DEFAULT_MAX_RETRIES, DEFAULT_TIMEOUT
from mcsrranked.resources.leaderboards import AsyncLeaderboards, Leaderboards
from mcsrranked.resources.live import AsyncLive, Live
from mcsrranked.resources.matches import AsyncMatches, Matches
from mcsrranked.resources.users import AsyncUsers, Users
from mcsrranked.resources.weekly_races import AsyncWeeklyRaces, WeeklyRaces

__all__ = ["MCSRRanked", "AsyncMCSRRanked"]


class MCSRRanked:
    """Synchronous client for the MCSR Ranked API.

    Usage:
        >>> client = MCSRRanked()
        >>> user = client.users.get("Couriway")
        >>> print(user.nickname, user.elo_rate)

        >>> # With context manager
        >>> with MCSRRanked() as client:
        ...     matches = client.matches.list()

        >>> # With API key for expanded rate limits
        >>> client = MCSRRanked(api_key="your-key")

        >>> # With private key for live data
        >>> client = MCSRRanked(private_key="your-private-key")
        >>> live = client.users.live("player")
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        private_key: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
    ) -> None:
        """Initialize the MCSR Ranked client.

        Args:
            api_key: API key for expanded rate limits.
                     Falls back to MCSRRANKED_API_KEY env var.
            private_key: Private key for accessing live data.
                         Falls back to MCSRRANKED_PRIVATE_KEY env var.
            base_url: Base URL for the API (default: https://api.mcsrranked.com).
            timeout: Request timeout in seconds (default: 30).
            max_retries: Maximum number of retries (default: 2).
        """
        self._api_key = api_key
        self._private_key = private_key
        self._base_url = base_url or BASE_URL
        self._timeout = timeout if timeout is not None else DEFAULT_TIMEOUT
        self._max_retries = (
            max_retries if max_retries is not None else DEFAULT_MAX_RETRIES
        )

        self._client = SyncAPIClient(
            base_url=self._base_url,
            api_key=self._api_key,
            private_key=self._private_key,
            timeout=self._timeout,
            max_retries=self._max_retries,
        )

    @cached_property
    def users(self) -> Users:
        """Users resource for user-related API calls."""
        return Users(self._client)

    @cached_property
    def matches(self) -> Matches:
        """Matches resource for match-related API calls."""
        return Matches(self._client)

    @cached_property
    def leaderboards(self) -> Leaderboards:
        """Leaderboards resource for leaderboard-related API calls."""
        return Leaderboards(self._client)

    @cached_property
    def live(self) -> Live:
        """Live resource for live data API calls."""
        return Live(self._client)

    @cached_property
    def weekly_races(self) -> WeeklyRaces:
        """Weekly races resource for weekly race API calls."""
        return WeeklyRaces(self._client)

    def with_options(
        self,
        *,
        api_key: str | None = None,
        private_key: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
    ) -> MCSRRanked:
        """Create a new client with modified options.

        Args:
            api_key: API key (default: inherit from current client).
            private_key: Private key (default: inherit from current client).
            base_url: Base URL (default: inherit from current client).
            timeout: Request timeout (default: inherit from current client).
            max_retries: Max retries (default: inherit from current client).

        Returns:
            New client instance with modified options.
        """
        return MCSRRanked(
            api_key=api_key if api_key is not None else self._api_key,
            private_key=private_key if private_key is not None else self._private_key,
            base_url=base_url if base_url is not None else self._base_url,
            timeout=timeout if timeout is not None else self._timeout,
            max_retries=max_retries if max_retries is not None else self._max_retries,
        )

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self) -> MCSRRanked:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


class AsyncMCSRRanked:
    """Asynchronous client for the MCSR Ranked API.

    Usage:
        >>> async with AsyncMCSRRanked() as client:
        ...     user = await client.users.get("Couriway")
        ...     print(user.nickname, user.elo_rate)

        >>> # With API key for expanded rate limits
        >>> async with AsyncMCSRRanked(api_key="your-key") as client:
        ...     matches = await client.matches.list()
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        private_key: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
    ) -> None:
        """Initialize the async MCSR Ranked client.

        Args:
            api_key: API key for expanded rate limits.
                     Falls back to MCSRRANKED_API_KEY env var.
            private_key: Private key for accessing live data.
                         Falls back to MCSRRANKED_PRIVATE_KEY env var.
            base_url: Base URL for the API (default: https://api.mcsrranked.com).
            timeout: Request timeout in seconds (default: 30).
            max_retries: Maximum number of retries (default: 2).
        """
        self._api_key = api_key
        self._private_key = private_key
        self._base_url = base_url or BASE_URL
        self._timeout = timeout if timeout is not None else DEFAULT_TIMEOUT
        self._max_retries = (
            max_retries if max_retries is not None else DEFAULT_MAX_RETRIES
        )

        self._client = AsyncAPIClient(
            base_url=self._base_url,
            api_key=self._api_key,
            private_key=self._private_key,
            timeout=self._timeout,
            max_retries=self._max_retries,
        )

    @cached_property
    def users(self) -> AsyncUsers:
        """Users resource for user-related API calls."""
        return AsyncUsers(self._client)

    @cached_property
    def matches(self) -> AsyncMatches:
        """Matches resource for match-related API calls."""
        return AsyncMatches(self._client)

    @cached_property
    def leaderboards(self) -> AsyncLeaderboards:
        """Leaderboards resource for leaderboard-related API calls."""
        return AsyncLeaderboards(self._client)

    @cached_property
    def live(self) -> AsyncLive:
        """Live resource for live data API calls."""
        return AsyncLive(self._client)

    @cached_property
    def weekly_races(self) -> AsyncWeeklyRaces:
        """Weekly races resource for weekly race API calls."""
        return AsyncWeeklyRaces(self._client)

    def with_options(
        self,
        *,
        api_key: str | None = None,
        private_key: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
    ) -> AsyncMCSRRanked:
        """Create a new client with modified options.

        Args:
            api_key: API key (default: inherit from current client).
            private_key: Private key (default: inherit from current client).
            base_url: Base URL (default: inherit from current client).
            timeout: Request timeout (default: inherit from current client).
            max_retries: Max retries (default: inherit from current client).

        Returns:
            New client instance with modified options.
        """
        return AsyncMCSRRanked(
            api_key=api_key if api_key is not None else self._api_key,
            private_key=private_key if private_key is not None else self._private_key,
            base_url=base_url if base_url is not None else self._base_url,
            timeout=timeout if timeout is not None else self._timeout,
            max_retries=max_retries if max_retries is not None else self._max_retries,
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.close()

    async def __aenter__(self) -> AsyncMCSRRanked:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
