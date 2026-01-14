# Matches

The Matches resource provides access to match data and detailed match information.

## List Recent Matches

```python
import mcsrranked
from mcsrranked import MatchType

# Get recent matches
matches = mcsrranked.matches.list()

# With filters
matches = mcsrranked.matches.list(
    count=50,              # Number of matches (1-100)
    type=MatchType.RANKED, # Filter by match type
    season=10,             # Specific season
    tag="tournament",      # Filter by tag
    includedecay=True,     # Include decay matches
)

# Pagination
matches = mcsrranked.matches.list(before=12345)
matches = mcsrranked.matches.list(after=12345)
```

## Match Types

```python
from mcsrranked import MatchType

MatchType.CASUAL   # 1 - Casual matches
MatchType.RANKED   # 2 - Ranked matches
MatchType.PRIVATE  # 3 - Private room matches
MatchType.EVENT    # 4 - Event mode matches
```

## Match Information

```python
for match in matches:
    print(f"ID: {match.id}")
    print(f"Type: {MatchType(match.type).name}")
    print(f"Season: {match.season}")
    print(f"Date: {match.date}")  # Unix timestamp in seconds

    # Players
    for player in match.players:
        print(f"  {player.nickname} ({player.elo_rate})")

    # Result
    if match.result:
        print(f"Winner: {match.result.uuid}")
        print(f"Time: {match.result.time}ms")

    # Elo changes
    for change in match.changes:
        print(f"  {change.uuid}: {change.change:+d}")
```

## Get Detailed Match Info

The `/matches/{id}` endpoint provides additional fields:

```python
match = mcsrranked.matches.get(12345)

# Basic info (same as list)
print(match.id, match.type, match.season)

# Advanced fields (only from get)
print(f"Replay exists: {match.replay_exist}")

# Timeline events
for event in match.timelines:
    print(f"{event.time}ms - {event.uuid}: {event.type}")

# Completions
for completion in match.completions:
    print(f"{completion.uuid} finished at {completion.time}ms")
```

## Seed Information

```python
if match.seed:
    print(f"Seed ID: {match.seed.id}")
    print(f"Overworld: {match.seed.overworld}")
    print(f"Bastion: {match.seed.bastion}")
    print(f"End Towers: {match.seed.end_towers}")
    print(f"Variations: {match.seed.variations}")
```

## VOD Information

```python
for vod in match.vod:
    print(f"Player: {vod.uuid}")
    print(f"URL: {vod.url}")
    print(f"Starts at: {vod.starts_at}")

    # Calculate timestamp
    timestamp = match.date - vod.starts_at
    print(f"Timestamp: {timestamp}s into stream")
```
