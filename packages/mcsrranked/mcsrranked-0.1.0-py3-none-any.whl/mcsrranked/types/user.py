from __future__ import annotations

from pydantic import BaseModel, Field

from mcsrranked.types.shared import Achievement

__all__ = [
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
]


class MatchTypeStats(BaseModel):
    """Statistics for a specific match type (ranked/casual)."""

    played_matches: int = Field(default=0, alias="playedMatches")
    wins: int = 0
    losses: int = 0
    draws: int = 0
    forfeits: int = 0
    highest_winstreak: int = Field(default=0, alias="highestWinstreak")
    current_winstreak: int = Field(default=0, alias="currentWinstreak")
    playtime: int = 0
    best_time: int | None = Field(default=None, alias="bestTime")
    best_time_id: int | None = Field(default=None, alias="bestTimeId")
    completions: int = 0

    model_config = {"populate_by_name": True}


class SeasonStats(BaseModel):
    """Season statistics container."""

    ranked: MatchTypeStats = Field(default_factory=MatchTypeStats)
    casual: MatchTypeStats = Field(default_factory=MatchTypeStats)

    model_config = {"populate_by_name": True}


class TotalStats(BaseModel):
    """All-time statistics container."""

    ranked: MatchTypeStats = Field(default_factory=MatchTypeStats)
    casual: MatchTypeStats = Field(default_factory=MatchTypeStats)

    model_config = {"populate_by_name": True}


class UserStatistics(BaseModel):
    """User statistics for season and total."""

    season: SeasonStats = Field(default_factory=SeasonStats)
    total: TotalStats = Field(default_factory=TotalStats)

    model_config = {"populate_by_name": True}


class UserTimestamps(BaseModel):
    """User activity timestamps."""

    first_online: int = Field(alias="firstOnline")
    last_online: int = Field(alias="lastOnline")
    last_ranked: int | None = Field(default=None, alias="lastRanked")
    next_decay: int | None = Field(default=None, alias="nextDecay")

    model_config = {"populate_by_name": True}


class PhaseResult(BaseModel):
    """Phase result data."""

    phase: int
    elo_rate: int = Field(alias="eloRate")
    elo_rank: int = Field(alias="eloRank")
    point: int

    model_config = {"populate_by_name": True}


class LastSeasonState(BaseModel):
    """Last state of a season."""

    elo_rate: int | None = Field(default=None, alias="eloRate")
    elo_rank: int | None = Field(default=None, alias="eloRank")
    phase_point: int | None = Field(default=None, alias="phasePoint")

    model_config = {"populate_by_name": True}


class SeasonResult(BaseModel):
    """User's season result data."""

    last: LastSeasonState
    highest: int | None = None
    lowest: int | None = None
    phases: list[PhaseResult] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


class Connection(BaseModel):
    """Third-party connection data."""

    id: str
    name: str

    model_config = {"populate_by_name": True}


class UserConnections(BaseModel):
    """User's third-party connections."""

    discord: Connection | None = None
    twitch: Connection | None = None
    youtube: Connection | None = None

    model_config = {"populate_by_name": True}


class WeeklyRaceResult(BaseModel):
    """User's weekly race result."""

    id: int
    time: int
    rank: int

    model_config = {"populate_by_name": True}


class AchievementsContainer(BaseModel):
    """Container for user achievements."""

    display: list[Achievement] = Field(default_factory=list)
    total: list[Achievement] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


class User(BaseModel):
    """Full user profile data."""

    uuid: str
    nickname: str
    role_type: int = Field(alias="roleType")
    elo_rate: int | None = Field(default=None, alias="eloRate")
    elo_rank: int | None = Field(default=None, alias="eloRank")
    country: str | None = None
    achievements: AchievementsContainer = Field(default_factory=AchievementsContainer)
    timestamp: UserTimestamps | None = None
    statistics: UserStatistics = Field(default_factory=UserStatistics)
    connections: UserConnections = Field(default_factory=UserConnections)
    season_result: SeasonResult | None = Field(default=None, alias="seasonResult")
    weekly_races: list[WeeklyRaceResult] = Field(
        default_factory=list, alias="weeklyRaces"
    )

    model_config = {"populate_by_name": True}


class SeasonResultEntry(BaseModel):
    """Season result entry for user seasons endpoint."""

    last: LastSeasonState
    highest: int
    lowest: int
    phases: list[PhaseResult] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


class UserSeasons(BaseModel):
    """User's season results across all seasons."""

    uuid: str
    nickname: str
    role_type: int = Field(alias="roleType")
    elo_rate: int | None = Field(default=None, alias="eloRate")
    elo_rank: int | None = Field(default=None, alias="eloRank")
    country: str | None = None
    season_results: dict[str, SeasonResultEntry] = Field(
        default_factory=dict, alias="seasonResults"
    )

    model_config = {"populate_by_name": True}
