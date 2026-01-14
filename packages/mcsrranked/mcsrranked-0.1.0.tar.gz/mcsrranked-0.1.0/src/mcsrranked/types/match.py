from __future__ import annotations

from pydantic import BaseModel, Field

from mcsrranked.types.shared import EloChange, MatchSeed, UserProfile, VodInfo

__all__ = [
    "MatchInfo",
    "MatchResult",
    "MatchRank",
    "Timeline",
    "Completion",
    "VersusStats",
    "VersusResults",
]


class MatchResult(BaseModel):
    """Match result data."""

    uuid: str | None = None
    time: int

    model_config = {"populate_by_name": True}


class MatchRank(BaseModel):
    """Match record ranking."""

    season: int | None = None
    all_time: int | None = Field(default=None, alias="allTime")

    model_config = {"populate_by_name": True}


class Timeline(BaseModel):
    """Match timeline event."""

    uuid: str
    time: int
    type: str

    model_config = {"populate_by_name": True}


class Completion(BaseModel):
    """Match completion data."""

    uuid: str
    time: int

    model_config = {"populate_by_name": True}


class MatchInfo(BaseModel):
    """Match information."""

    id: int
    type: int
    season: int
    category: str | None = None
    date: int
    players: list[UserProfile] = Field(default_factory=list)
    spectators: list[UserProfile] = Field(default_factory=list)
    seed: MatchSeed | None = None
    result: MatchResult | None = None
    forfeited: bool = False
    decayed: bool = False
    rank: MatchRank | None = None
    changes: list[EloChange] = Field(default_factory=list)
    tag: str | None = None
    beginner: bool = False
    vod: list[VodInfo] = Field(default_factory=list)
    # Advanced fields (only from /matches/{id} endpoint)
    completions: list[Completion] = Field(default_factory=list)
    timelines: list[Timeline] = Field(default_factory=list)
    replay_exist: bool = Field(default=False, alias="replayExist")

    model_config = {"populate_by_name": True}


class VersusResultStats(BaseModel):
    """Stats for versus results."""

    total: int = 0

    model_config = {"populate_by_name": True, "extra": "allow"}


class VersusResults(BaseModel):
    """Versus match results."""

    ranked: dict[str, int] = Field(default_factory=dict)
    casual: dict[str, int] = Field(default_factory=dict)

    model_config = {"populate_by_name": True}


class VersusStats(BaseModel):
    """Versus statistics between two players."""

    players: list[UserProfile] = Field(default_factory=list)
    results: VersusResults = Field(default_factory=VersusResults)
    changes: dict[str, int] = Field(default_factory=dict)

    model_config = {"populate_by_name": True}
