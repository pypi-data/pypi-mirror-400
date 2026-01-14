from __future__ import annotations

from typing import TYPE_CHECKING

from mcsrranked.types.leaderboard import (
    EloLeaderboard,
    PhaseLeaderboard,
    RecordEntry,
)

if TYPE_CHECKING:
    from mcsrranked._base_client import AsyncAPIClient, SyncAPIClient

__all__ = ["Leaderboards", "AsyncLeaderboards"]


class Leaderboards:
    """Synchronous leaderboards resource."""

    def __init__(self, client: SyncAPIClient) -> None:
        self._client = client

    def elo(
        self,
        *,
        season: int | None = None,
        country: str | None = None,
    ) -> EloLeaderboard:
        """Get Elo leaderboard.

        Returns top 150 players by Elo rating.

        Args:
            season: Specific season (default: current season).
            country: Filter by country code (ISO 3166-1 alpha-2, lowercase).

        Returns:
            Elo leaderboard data.
        """
        params = {"season": season, "country": country}
        data = self._client.get("/leaderboard", params=params)
        return EloLeaderboard.model_validate(data["data"])

    def phase(
        self,
        *,
        season: int | None = None,
        country: str | None = None,
        predicted: bool = False,
    ) -> PhaseLeaderboard:
        """Get phase points leaderboard.

        Returns top 100 players by phase points.

        Args:
            season: Specific season (default: current season).
            country: Filter by country code (ISO 3166-1 alpha-2, lowercase).
            predicted: Get predicted phase points (only works with current season).

        Returns:
            Phase points leaderboard data.
        """
        params = {
            "season": season,
            "country": country,
            "predicted": "" if predicted else None,
        }
        data = self._client.get("/phase-leaderboard", params=params)
        return PhaseLeaderboard.model_validate(data["data"])

    def record(
        self,
        *,
        season: int | None = None,
        distinct: bool = False,
    ) -> list[RecordEntry]:
        """Get best time leaderboard.

        Args:
            season: Specific season. Use 0 for current season,
                    None for all-time records.
            distinct: Only show fastest run per player.

        Returns:
            List of record entries.
        """
        params = {
            "season": season,
            "distinct": "" if distinct else None,
        }
        data = self._client.get("/record-leaderboard", params=params)
        return [RecordEntry.model_validate(r) for r in data["data"]]


class AsyncLeaderboards:
    """Asynchronous leaderboards resource."""

    def __init__(self, client: AsyncAPIClient) -> None:
        self._client = client

    async def elo(
        self,
        *,
        season: int | None = None,
        country: str | None = None,
    ) -> EloLeaderboard:
        """Get Elo leaderboard.

        Returns top 150 players by Elo rating.

        Args:
            season: Specific season (default: current season).
            country: Filter by country code (ISO 3166-1 alpha-2, lowercase).

        Returns:
            Elo leaderboard data.
        """
        params = {"season": season, "country": country}
        data = await self._client.get("/leaderboard", params=params)
        return EloLeaderboard.model_validate(data["data"])

    async def phase(
        self,
        *,
        season: int | None = None,
        country: str | None = None,
        predicted: bool = False,
    ) -> PhaseLeaderboard:
        """Get phase points leaderboard.

        Returns top 100 players by phase points.

        Args:
            season: Specific season (default: current season).
            country: Filter by country code (ISO 3166-1 alpha-2, lowercase).
            predicted: Get predicted phase points (only works with current season).

        Returns:
            Phase points leaderboard data.
        """
        params = {
            "season": season,
            "country": country,
            "predicted": "" if predicted else None,
        }
        data = await self._client.get("/phase-leaderboard", params=params)
        return PhaseLeaderboard.model_validate(data["data"])

    async def record(
        self,
        *,
        season: int | None = None,
        distinct: bool = False,
    ) -> list[RecordEntry]:
        """Get best time leaderboard.

        Args:
            season: Specific season. Use 0 for current season,
                    None for all-time records.
            distinct: Only show fastest run per player.

        Returns:
            List of record entries.
        """
        params = {
            "season": season,
            "distinct": "" if distinct else None,
        }
        data = await self._client.get("/record-leaderboard", params=params)
        return [RecordEntry.model_validate(r) for r in data["data"]]
