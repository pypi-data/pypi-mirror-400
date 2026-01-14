"""MCSR Ranked API Python SDK.

A modern Python SDK for the MCSR Ranked API.

Usage:
    >>> import mcsrranked
    >>> user = mcsrranked.users.get("Couriway")
    >>> print(user.nickname, user.elo_rate)

    >>> # Or with explicit client
    >>> from mcsrranked import MCSRRanked
    >>> client = MCSRRanked()
    >>> matches = client.matches.list()

    >>> # Async usage
    >>> from mcsrranked import AsyncMCSRRanked
    >>> async with AsyncMCSRRanked() as client:
    ...     user = await client.users.get("Couriway")
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from mcsrranked._client import AsyncMCSRRanked, MCSRRanked
from mcsrranked._exceptions import (
    APIConnectionError,
    APIError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    MCSRRankedError,
    NotFoundError,
    RateLimitError,
)
from mcsrranked._types import MatchType, SortOrder
from mcsrranked.types import (
    Achievement,
    Completion,
    Connection,
    EloChange,
    EloLeaderboard,
    LeaderboardUser,
    LiveData,
    LiveMatch,
    LiveMatchPlayer,
    LivePlayerTimeline,
    MatchInfo,
    MatchRank,
    MatchResult,
    MatchSeed,
    MatchTypeStats,
    PhaseInfo,
    PhaseLeaderboard,
    PhaseLeaderboardUser,
    PhaseResult,
    RaceLeaderboardEntry,
    RecordEntry,
    SeasonInfo,
    SeasonResult,
    Timeline,
    User,
    UserConnections,
    UserLiveMatch,
    UserProfile,
    UserSeasons,
    UserStatistics,
    UserTimestamps,
    VersusResults,
    VersusStats,
    VodInfo,
    WeeklyRace,
    WeeklyRaceResult,
    WeeklyRaceSeed,
)

if TYPE_CHECKING:
    from mcsrranked.resources import (
        Leaderboards,
        Live,
        Matches,
        Users,
        WeeklyRaces,
    )

__version__ = "0.1.0"

__all__ = [
    # Version
    "__version__",
    # Clients
    "MCSRRanked",
    "AsyncMCSRRanked",
    # Exceptions
    "MCSRRankedError",
    "APIError",
    "APIStatusError",
    "APIConnectionError",
    "APITimeoutError",
    "BadRequestError",
    "AuthenticationError",
    "NotFoundError",
    "RateLimitError",
    # Types
    "MatchType",
    "SortOrder",
    # Models - shared
    "UserProfile",
    "Achievement",
    "MatchSeed",
    "EloChange",
    "VodInfo",
    # Models - user
    "User",
    "UserTimestamps",
    "UserStatistics",
    "MatchTypeStats",
    "SeasonResult",
    "PhaseResult",
    "Connection",
    "UserConnections",
    "WeeklyRaceResult",
    "UserSeasons",
    # Models - match
    "MatchInfo",
    "MatchResult",
    "MatchRank",
    "Timeline",
    "Completion",
    "VersusStats",
    "VersusResults",
    # Models - leaderboard
    "SeasonInfo",
    "LeaderboardUser",
    "EloLeaderboard",
    "PhaseInfo",
    "PhaseLeaderboardUser",
    "PhaseLeaderboard",
    "RecordEntry",
    # Models - live
    "LiveData",
    "LiveMatch",
    "LiveMatchPlayer",
    "LivePlayerTimeline",
    "UserLiveMatch",
    # Models - weekly_race
    "WeeklyRace",
    "WeeklyRaceSeed",
    "RaceLeaderboardEntry",
    # Module-level resources
    "users",
    "matches",
    "leaderboards",
    "live",
    "weekly_races",
]


# Module-level client for convenient access
_client: MCSRRanked | None = None


def _get_client() -> MCSRRanked:
    """Get or create the module-level client."""
    global _client
    if _client is None:
        _client = MCSRRanked()
    return _client


class _UsersProxy:
    """Proxy for module-level users access."""

    def __getattr__(self, name: str) -> object:
        return getattr(_get_client().users, name)


class _MatchesProxy:
    """Proxy for module-level matches access."""

    def __getattr__(self, name: str) -> object:
        return getattr(_get_client().matches, name)


class _LeaderboardsProxy:
    """Proxy for module-level leaderboards access."""

    def __getattr__(self, name: str) -> object:
        return getattr(_get_client().leaderboards, name)


class _LiveProxy:
    """Proxy for module-level live access."""

    def __getattr__(self, name: str) -> object:
        return getattr(_get_client().live, name)


class _WeeklyRacesProxy:
    """Proxy for module-level weekly_races access."""

    def __getattr__(self, name: str) -> object:
        return getattr(_get_client().weekly_races, name)


# Module-level resource proxies
users: Users = _UsersProxy()  # type: ignore[assignment]
matches: Matches = _MatchesProxy()  # type: ignore[assignment]
leaderboards: Leaderboards = _LeaderboardsProxy()  # type: ignore[assignment]
live: Live = _LiveProxy()  # type: ignore[assignment]
weekly_races: WeeklyRaces = _WeeklyRacesProxy()  # type: ignore[assignment]
