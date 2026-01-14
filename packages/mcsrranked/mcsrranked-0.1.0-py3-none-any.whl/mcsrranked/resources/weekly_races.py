from __future__ import annotations

from typing import TYPE_CHECKING

from mcsrranked.types.weekly_race import WeeklyRace

if TYPE_CHECKING:
    from mcsrranked._base_client import AsyncAPIClient, SyncAPIClient

__all__ = ["WeeklyRaces", "AsyncWeeklyRaces"]


class WeeklyRaces:
    """Synchronous weekly races resource."""

    def __init__(self, client: SyncAPIClient) -> None:
        self._client = client

    def get(self, race_id: int | None = None) -> WeeklyRace:
        """Get weekly race info and leaderboard.

        Args:
            race_id: Specific week number. If None, returns current race.

        Returns:
            Weekly race data including leaderboard.
        """
        path = f"/weekly-race/{race_id}" if race_id is not None else "/weekly-race"
        data = self._client.get(path)
        return WeeklyRace.model_validate(data["data"])


class AsyncWeeklyRaces:
    """Asynchronous weekly races resource."""

    def __init__(self, client: AsyncAPIClient) -> None:
        self._client = client

    async def get(self, race_id: int | None = None) -> WeeklyRace:
        """Get weekly race info and leaderboard.

        Args:
            race_id: Specific week number. If None, returns current race.

        Returns:
            Weekly race data including leaderboard.
        """
        path = f"/weekly-race/{race_id}" if race_id is not None else "/weekly-race"
        data = await self._client.get(path)
        return WeeklyRace.model_validate(data["data"])
