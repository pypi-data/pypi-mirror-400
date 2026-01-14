from __future__ import annotations

from typing import TYPE_CHECKING

from mcsrranked._types import MatchType
from mcsrranked.types.match import MatchInfo

if TYPE_CHECKING:
    from mcsrranked._base_client import AsyncAPIClient, SyncAPIClient

__all__ = ["Matches", "AsyncMatches"]


class Matches:
    """Synchronous matches resource."""

    def __init__(self, client: SyncAPIClient) -> None:
        self._client = client

    def list(
        self,
        *,
        before: int | None = None,
        after: int | None = None,
        count: int = 20,
        type: MatchType | int | None = None,
        tag: str | None = None,
        season: int | None = None,
        includedecay: bool = False,
    ) -> list[MatchInfo]:
        """Get recent matches.

        Args:
            before: Get matches before this match ID (cursor).
            after: Get matches after this match ID (cursor).
            count: Number of matches per page (1-100, default: 20).
            type: Filter by match type.
            tag: Filter by match tag.
            season: Specific season (default: current season).
            includedecay: Include decayed matches.

        Returns:
            List of match info.
        """
        params = {
            "before": before,
            "after": after,
            "count": count,
            "type": int(type) if type is not None else None,
            "tag": tag,
            "season": season,
            "includedecay": "" if includedecay else None,
        }
        data = self._client.get("/matches", params=params)
        return [MatchInfo.model_validate(m) for m in data["data"]]

    def get(self, match_id: int) -> MatchInfo:
        """Get detailed match information.

        Args:
            match_id: The match ID.

        Returns:
            Detailed match info including timelines and completions.
        """
        data = self._client.get(f"/matches/{match_id}")
        return MatchInfo.model_validate(data["data"])


class AsyncMatches:
    """Asynchronous matches resource."""

    def __init__(self, client: AsyncAPIClient) -> None:
        self._client = client

    async def list(
        self,
        *,
        before: int | None = None,
        after: int | None = None,
        count: int = 20,
        type: MatchType | int | None = None,
        tag: str | None = None,
        season: int | None = None,
        includedecay: bool = False,
    ) -> list[MatchInfo]:
        """Get recent matches.

        Args:
            before: Get matches before this match ID (cursor).
            after: Get matches after this match ID (cursor).
            count: Number of matches per page (1-100, default: 20).
            type: Filter by match type.
            tag: Filter by match tag.
            season: Specific season (default: current season).
            includedecay: Include decayed matches.

        Returns:
            List of match info.
        """
        params = {
            "before": before,
            "after": after,
            "count": count,
            "type": int(type) if type is not None else None,
            "tag": tag,
            "season": season,
            "includedecay": "" if includedecay else None,
        }
        data = await self._client.get("/matches", params=params)
        return [MatchInfo.model_validate(m) for m in data["data"]]

    async def get(self, match_id: int) -> MatchInfo:
        """Get detailed match information.

        Args:
            match_id: The match ID.

        Returns:
            Detailed match info including timelines and completions.
        """
        data = await self._client.get(f"/matches/{match_id}")
        return MatchInfo.model_validate(data["data"])
