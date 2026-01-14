# Types Reference

All API responses are parsed into Pydantic models with full type hints.

## Enums

### MatchType

```python
from mcsrranked import MatchType

MatchType.CASUAL   # 1
MatchType.RANKED   # 2
MatchType.PRIVATE  # 3
MatchType.EVENT    # 4
```

### SortOrder

```python
from mcsrranked import SortOrder

# Type alias for: Literal["newest", "oldest", "fastest", "slowest"]
```

---

## User Types

### User

Full user profile data.

| Field | Type | Description |
|-------|------|-------------|
| `uuid` | `str` | UUID without dashes |
| `nickname` | `str` | Display name |
| `elo_rate` | `int \| None` | Current elo rating |
| `elo_rank` | `int \| None` | Current rank |
| `country` | `str \| None` | Country code (ISO 3166-1 alpha-2) |
| `role_type` | `int` | User role type |
| `achievements` | `AchievementsContainer` | User achievements |
| `timestamp` | `UserTimestamps \| None` | Activity timestamps |
| `statistics` | `UserStatistics` | Season and total stats |
| `connections` | `UserConnections` | Third-party connections |
| `season_result` | `SeasonResult \| None` | Current season data |
| `weekly_races` | `list[WeeklyRaceResult]` | Weekly race results |

### UserProfile

Basic user profile (used in matches, leaderboards).

| Field | Type | Description |
|-------|------|-------------|
| `uuid` | `str` | UUID without dashes |
| `nickname` | `str` | Display name |
| `elo_rate` | `int \| None` | Elo rating |
| `elo_rank` | `int \| None` | Rank |
| `country` | `str \| None` | Country code |
| `role_type` | `int` | Role type |

### UserStatistics

| Field | Type |
|-------|------|
| `season` | `SeasonStats` |
| `total` | `TotalStats` |

### MatchTypeStats

Statistics for ranked/casual matches.

| Field | Type |
|-------|------|
| `played_matches` | `int` |
| `wins` | `int` |
| `losses` | `int` |
| `draws` | `int` |
| `forfeits` | `int` |
| `highest_winstreak` | `int` |
| `current_winstreak` | `int` |
| `playtime` | `int` |
| `best_time` | `int \| None` |
| `best_time_id` | `int \| None` |
| `completions` | `int` |

---

## Match Types

### MatchInfo

| Field | Type | Description |
|-------|------|-------------|
| `id` | `int` | Match ID |
| `type` | `int` | Match type (1-4) |
| `season` | `int` | Season number |
| `category` | `str \| None` | Completion category |
| `date` | `int` | Unix timestamp (seconds) |
| `players` | `list[UserProfile]` | Match players |
| `spectators` | `list[UserProfile]` | Match spectators |
| `seed` | `MatchSeed \| None` | Seed information |
| `result` | `MatchResult \| None` | Match result |
| `forfeited` | `bool` | No completions |
| `decayed` | `bool` | Decayed match |
| `rank` | `MatchRank \| None` | Record ranking |
| `changes` | `list[EloChange]` | Elo changes |
| `tag` | `str \| None` | Special tag |
| `beginner` | `bool` | Beginner mode |
| `vod` | `list[VodInfo]` | VOD information |
| `completions` | `list[Completion]` | (Advanced) Completions |
| `timelines` | `list[Timeline]` | (Advanced) Timeline events |
| `replay_exist` | `bool` | (Advanced) Replay available |

### MatchSeed

| Field | Type |
|-------|------|
| `id` | `str \| None` |
| `overworld` | `str \| None` |
| `bastion` | `str \| None` |
| `end_towers` | `list[int]` |
| `variations` | `list[str]` |

### MatchResult

| Field | Type |
|-------|------|
| `uuid` | `str \| None` |
| `time` | `int` |

### Timeline

| Field | Type |
|-------|------|
| `uuid` | `str` |
| `time` | `int` |
| `type` | `str` |

---

## Leaderboard Types

### EloLeaderboard

| Field | Type |
|-------|------|
| `season` | `SeasonInfo` |
| `users` | `list[LeaderboardUser]` |

### PhaseLeaderboard

| Field | Type |
|-------|------|
| `phase` | `PhaseInfo` |
| `users` | `list[PhaseLeaderboardUser]` |

### RecordEntry

| Field | Type |
|-------|------|
| `rank` | `int` |
| `season` | `int` |
| `date` | `int` |
| `id` | `int` |
| `time` | `int` |
| `user` | `UserProfile` |
| `seed` | `MatchSeed \| None` |

---

## Live Types

### LiveData

| Field | Type |
|-------|------|
| `players` | `int` |
| `live_matches` | `list[LiveMatch]` |

### UserLiveMatch

| Field | Type |
|-------|------|
| `last_id` | `int \| None` |
| `type` | `int` |
| `status` | `str` |
| `time` | `int` |
| `players` | `list[UserProfile]` |
| `spectators` | `list[UserProfile]` |
| `timelines` | `list[Timeline]` |
| `completions` | `list[Completion]` |

---

## Weekly Race Types

### WeeklyRace

| Field | Type |
|-------|------|
| `id` | `int` |
| `seed` | `WeeklyRaceSeed` |
| `ends_at` | `int` |
| `leaderboard` | `list[RaceLeaderboardEntry]` |

### RaceLeaderboardEntry

| Field | Type |
|-------|------|
| `rank` | `int` |
| `player` | `UserProfile` |
| `time` | `int` |
| `replay_exist` | `bool` |
