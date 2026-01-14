from __future__ import annotations

from pydantic import BaseModel, Field

__all__ = [
    "UserProfile",
    "Achievement",
    "MatchSeed",
    "EloChange",
    "VodInfo",
]


class UserProfile(BaseModel):
    """Basic user profile information."""

    uuid: str
    nickname: str
    role_type: int = Field(alias="roleType")
    elo_rate: int | None = Field(default=None, alias="eloRate")
    elo_rank: int | None = Field(default=None, alias="eloRank")
    country: str | None = None

    model_config = {"populate_by_name": True}


class Achievement(BaseModel):
    """User achievement data."""

    id: str
    date: int
    data: list[str | int] = Field(default_factory=list)
    level: int
    value: int | None = None
    goal: int | None = None

    model_config = {"populate_by_name": True}


class MatchSeed(BaseModel):
    """Match seed information."""

    id: str | None = None
    overworld: str | None = None
    bastion: str | None = None
    end_towers: list[int] = Field(default_factory=list, alias="endTowers")
    variations: list[str] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


class EloChange(BaseModel):
    """Elo change data for a player in a match."""

    uuid: str
    change: int | None = None
    elo_rate: int | None = Field(default=None, alias="eloRate")

    model_config = {"populate_by_name": True}


class VodInfo(BaseModel):
    """VOD information for a match."""

    uuid: str
    url: str
    starts_at: int = Field(alias="startsAt")

    model_config = {"populate_by_name": True}
