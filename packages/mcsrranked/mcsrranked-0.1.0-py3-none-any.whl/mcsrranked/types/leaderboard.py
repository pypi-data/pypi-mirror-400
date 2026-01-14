from __future__ import annotations

from pydantic import BaseModel, Field

from mcsrranked.types.shared import MatchSeed, UserProfile

__all__ = [
    "SeasonInfo",
    "LeaderboardUser",
    "EloLeaderboard",
    "PhaseInfo",
    "PhaseLeaderboardUser",
    "PhaseLeaderboard",
    "RecordEntry",
]


class SeasonInfo(BaseModel):
    """Season information."""

    number: int
    starts_at: int = Field(alias="startsAt")
    ends_at: int = Field(alias="endsAt")

    model_config = {"populate_by_name": True}


class LeaderboardSeasonResult(BaseModel):
    """Season result for leaderboard user."""

    elo_rate: int = Field(alias="eloRate")
    elo_rank: int = Field(alias="eloRank")
    phase_point: int = Field(alias="phasePoint")

    model_config = {"populate_by_name": True}


class LeaderboardUser(UserProfile):
    """User entry in the elo leaderboard."""

    season_result: LeaderboardSeasonResult = Field(alias="seasonResult")

    model_config = {"populate_by_name": True}


class EloLeaderboard(BaseModel):
    """Elo leaderboard data."""

    season: SeasonInfo
    users: list[LeaderboardUser] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


class PhaseInfo(BaseModel):
    """Phase information."""

    season: int
    number: int | None = None
    ends_at: int | None = Field(default=None, alias="endsAt")

    model_config = {"populate_by_name": True}


class PhaseLeaderboardUser(UserProfile):
    """User entry in the phase points leaderboard."""

    season_result: LeaderboardSeasonResult = Field(alias="seasonResult")
    pred_phase_point: int = Field(default=0, alias="predPhasePoint")

    model_config = {"populate_by_name": True}


class PhaseLeaderboard(BaseModel):
    """Phase points leaderboard data."""

    phase: PhaseInfo
    users: list[PhaseLeaderboardUser] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


class RecordEntry(BaseModel):
    """Record leaderboard entry."""

    rank: int
    season: int
    date: int
    id: int
    time: int
    user: UserProfile
    seed: MatchSeed | None = None

    model_config = {"populate_by_name": True}
