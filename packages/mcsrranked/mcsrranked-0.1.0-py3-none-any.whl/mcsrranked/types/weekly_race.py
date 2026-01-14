from __future__ import annotations

from pydantic import BaseModel, Field

from mcsrranked.types.shared import UserProfile

__all__ = [
    "WeeklyRace",
    "WeeklyRaceSeed",
    "RaceLeaderboardEntry",
]


class WeeklyRaceSeed(BaseModel):
    """Weekly race seed information."""

    overworld: str | None = None
    nether: str | None = None
    the_end: str | None = Field(default=None, alias="theEnd")
    rng: str | None = None

    model_config = {"populate_by_name": True}


class RaceLeaderboardEntry(BaseModel):
    """Entry in the weekly race leaderboard."""

    rank: int
    player: UserProfile
    time: int
    replay_exist: bool = Field(default=False, alias="replayExist")

    model_config = {"populate_by_name": True}


class WeeklyRace(BaseModel):
    """Weekly race data."""

    id: int
    seed: WeeklyRaceSeed
    ends_at: int = Field(alias="endsAt")
    leaderboard: list[RaceLeaderboardEntry] = Field(default_factory=list)

    model_config = {"populate_by_name": True}
