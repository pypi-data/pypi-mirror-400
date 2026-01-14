from __future__ import annotations

from pydantic import BaseModel, Field

from mcsrranked.types.match import Completion, Timeline
from mcsrranked.types.shared import UserProfile

__all__ = [
    "LiveData",
    "LiveMatch",
    "LiveMatchPlayer",
    "LivePlayerTimeline",
    "UserLiveMatch",
]


class LivePlayerTimeline(BaseModel):
    """Live player timeline data."""

    time: int
    type: str

    model_config = {"populate_by_name": True}


class LivePlayerData(BaseModel):
    """Live player data in a match."""

    live_url: str | None = Field(default=None, alias="liveUrl")
    timeline: LivePlayerTimeline | None = None

    model_config = {"populate_by_name": True}


class LiveMatch(BaseModel):
    """Live match data."""

    current_time: int = Field(alias="currentTime")
    players: list[UserProfile] = Field(default_factory=list)
    data: dict[str, LivePlayerData] = Field(default_factory=dict)

    model_config = {"populate_by_name": True}


class LiveMatchPlayer(UserProfile):
    """Player in a live match with stream data."""

    live_url: str | None = Field(default=None, alias="liveUrl")

    model_config = {"populate_by_name": True}


class LiveData(BaseModel):
    """Live data response."""

    players: int
    live_matches: list[LiveMatch] = Field(default_factory=list, alias="liveMatches")

    model_config = {"populate_by_name": True}


class UserLiveMatch(BaseModel):
    """Live match data for a specific user (from /users/{id}/live endpoint)."""

    last_id: int | None = Field(default=None, alias="lastId")
    type: int
    status: str
    time: int
    players: list[UserProfile] = Field(default_factory=list)
    spectators: list[UserProfile] = Field(default_factory=list)
    timelines: list[Timeline] = Field(default_factory=list)
    completions: list[Completion] = Field(default_factory=list)

    model_config = {"populate_by_name": True}
