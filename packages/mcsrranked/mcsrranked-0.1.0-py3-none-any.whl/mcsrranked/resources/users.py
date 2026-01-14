from __future__ import annotations

from typing import TYPE_CHECKING

from mcsrranked._types import MatchType, SortOrder
from mcsrranked.types.live import UserLiveMatch
from mcsrranked.types.match import MatchInfo, VersusStats
from mcsrranked.types.user import User, UserSeasons

if TYPE_CHECKING:
    from mcsrranked._base_client import AsyncAPIClient, SyncAPIClient

__all__ = ["Users", "AsyncUsers"]


class Users:
    """Synchronous users resource."""

    def __init__(self, client: SyncAPIClient) -> None:
        self._client = client

    def get(self, identifier: str, *, season: int | None = None) -> User:
        """Get user data by UUID, nickname, or Discord ID.

        Args:
            identifier: User UUID, nickname, or Discord ID (format: discord.{id}).
            season: Specific season for statistics (default: current season).

        Returns:
            User profile data.
        """
        params = {"season": season}
        data = self._client.get(f"/users/{identifier}", params=params)
        return User.model_validate(data["data"])

    def matches(
        self,
        identifier: str,
        *,
        before: int | None = None,
        after: int | None = None,
        sort: SortOrder = "newest",
        count: int = 20,
        type: MatchType | int | None = None,
        season: int | None = None,
        excludedecay: bool = False,
    ) -> list[MatchInfo]:
        """Get user's match history.

        Args:
            identifier: User UUID, nickname, or Discord ID.
            before: Get matches before this match ID (cursor).
            after: Get matches after this match ID (cursor).
            sort: Sort order (newest, oldest, fastest, slowest).
            count: Number of matches per page (1-100, default: 20).
            type: Filter by match type.
            season: Specific season (default: current season).
            excludedecay: Exclude decayed matches.

        Returns:
            List of match info.
        """
        params = {
            "before": before,
            "after": after,
            "sort": sort,
            "count": count,
            "type": int(type) if type is not None else None,
            "season": season,
            "excludedecay": excludedecay if excludedecay else None,
        }
        data = self._client.get(f"/users/{identifier}/matches", params=params)
        return [MatchInfo.model_validate(m) for m in data["data"]]

    def seasons(self, identifier: str) -> UserSeasons:
        """Get all season results for a user.

        Args:
            identifier: User UUID, nickname, or Discord ID.

        Returns:
            User's season results across all seasons.
        """
        data = self._client.get(f"/users/{identifier}/seasons")
        return UserSeasons.model_validate(data["data"])

    def live(self, identifier: str) -> UserLiveMatch:
        """Get live match data for a user.

        Requires private_key to be set.

        Args:
            identifier: User UUID, nickname, or Discord ID.

        Returns:
            Live match data if user is in a match.
        """
        data = self._client.get(f"/users/{identifier}/live", require_private_key=True)
        return UserLiveMatch.model_validate(data["data"])

    def versus(
        self,
        identifier: str,
        other: str,
        *,
        season: int | None = None,
    ) -> VersusStats:
        """Get versus stats between two players.

        Args:
            identifier: First user UUID, nickname, or Discord ID.
            other: Second user UUID, nickname, or Discord ID.
            season: Specific season (default: current season).

        Returns:
            Versus statistics.
        """
        params = {"season": season}
        data = self._client.get(f"/users/{identifier}/versus/{other}", params=params)
        return VersusStats.model_validate(data["data"])

    def versus_matches(
        self,
        identifier: str,
        other: str,
        *,
        before: int | None = None,
        after: int | None = None,
        count: int = 20,
        type: MatchType | int | None = None,
        season: int | None = None,
    ) -> list[MatchInfo]:
        """Get match history between two players.

        Args:
            identifier: First user UUID, nickname, or Discord ID.
            other: Second user UUID, nickname, or Discord ID.
            before: Get matches before this match ID (cursor).
            after: Get matches after this match ID (cursor).
            count: Number of matches per page (1-100, default: 20).
            type: Filter by match type.
            season: Specific season (default: current season).

        Returns:
            List of match info.
        """
        params = {
            "before": before,
            "after": after,
            "count": count,
            "type": int(type) if type is not None else None,
            "season": season,
        }
        data = self._client.get(
            f"/users/{identifier}/versus/{other}/matches", params=params
        )
        return [MatchInfo.model_validate(m) for m in data["data"]]


class AsyncUsers:
    """Asynchronous users resource."""

    def __init__(self, client: AsyncAPIClient) -> None:
        self._client = client

    async def get(self, identifier: str, *, season: int | None = None) -> User:
        """Get user data by UUID, nickname, or Discord ID.

        Args:
            identifier: User UUID, nickname, or Discord ID (format: discord.{id}).
            season: Specific season for statistics (default: current season).

        Returns:
            User profile data.
        """
        params = {"season": season}
        data = await self._client.get(f"/users/{identifier}", params=params)
        return User.model_validate(data["data"])

    async def matches(
        self,
        identifier: str,
        *,
        before: int | None = None,
        after: int | None = None,
        sort: SortOrder = "newest",
        count: int = 20,
        type: MatchType | int | None = None,
        season: int | None = None,
        excludedecay: bool = False,
    ) -> list[MatchInfo]:
        """Get user's match history.

        Args:
            identifier: User UUID, nickname, or Discord ID.
            before: Get matches before this match ID (cursor).
            after: Get matches after this match ID (cursor).
            sort: Sort order (newest, oldest, fastest, slowest).
            count: Number of matches per page (1-100, default: 20).
            type: Filter by match type.
            season: Specific season (default: current season).
            excludedecay: Exclude decayed matches.

        Returns:
            List of match info.
        """
        params = {
            "before": before,
            "after": after,
            "sort": sort,
            "count": count,
            "type": int(type) if type is not None else None,
            "season": season,
            "excludedecay": excludedecay if excludedecay else None,
        }
        data = await self._client.get(f"/users/{identifier}/matches", params=params)
        return [MatchInfo.model_validate(m) for m in data["data"]]

    async def seasons(self, identifier: str) -> UserSeasons:
        """Get all season results for a user.

        Args:
            identifier: User UUID, nickname, or Discord ID.

        Returns:
            User's season results across all seasons.
        """
        data = await self._client.get(f"/users/{identifier}/seasons")
        return UserSeasons.model_validate(data["data"])

    async def live(self, identifier: str) -> UserLiveMatch:
        """Get live match data for a user.

        Requires private_key to be set.

        Args:
            identifier: User UUID, nickname, or Discord ID.

        Returns:
            Live match data if user is in a match.
        """
        data = await self._client.get(
            f"/users/{identifier}/live", require_private_key=True
        )
        return UserLiveMatch.model_validate(data["data"])

    async def versus(
        self,
        identifier: str,
        other: str,
        *,
        season: int | None = None,
    ) -> VersusStats:
        """Get versus stats between two players.

        Args:
            identifier: First user UUID, nickname, or Discord ID.
            other: Second user UUID, nickname, or Discord ID.
            season: Specific season (default: current season).

        Returns:
            Versus statistics.
        """
        params = {"season": season}
        data = await self._client.get(
            f"/users/{identifier}/versus/{other}", params=params
        )
        return VersusStats.model_validate(data["data"])

    async def versus_matches(
        self,
        identifier: str,
        other: str,
        *,
        before: int | None = None,
        after: int | None = None,
        count: int = 20,
        type: MatchType | int | None = None,
        season: int | None = None,
    ) -> list[MatchInfo]:
        """Get match history between two players.

        Args:
            identifier: First user UUID, nickname, or Discord ID.
            other: Second user UUID, nickname, or Discord ID.
            before: Get matches before this match ID (cursor).
            after: Get matches after this match ID (cursor).
            count: Number of matches per page (1-100, default: 20).
            type: Filter by match type.
            season: Specific season (default: current season).

        Returns:
            List of match info.
        """
        params = {
            "before": before,
            "after": after,
            "count": count,
            "type": int(type) if type is not None else None,
            "season": season,
        }
        data = await self._client.get(
            f"/users/{identifier}/versus/{other}/matches", params=params
        )
        return [MatchInfo.model_validate(m) for m in data["data"]]
