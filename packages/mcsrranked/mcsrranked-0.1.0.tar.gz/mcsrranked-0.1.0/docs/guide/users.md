# Users

The Users resource provides access to user profiles, match history, season results, and versus statistics.

## Get User Profile

Fetch a user's profile by UUID, nickname, or Discord ID:

```python
import mcsrranked

# By nickname
user = mcsrranked.users.get("Feinberg")

# By UUID
user = mcsrranked.users.get("3c8757790ab0400b8b9e3936e0dd535b")

# By Discord ID
user = mcsrranked.users.get("discord.338669823167037440")
```

### User Fields

```python
user = mcsrranked.users.get("Feinberg")

print(user.uuid)           # UUID without dashes
print(user.nickname)       # Display name
print(user.elo_rate)       # Current elo (None if unranked)
print(user.elo_rank)       # Current rank (None if unranked)
print(user.country)        # Country code (ISO 3166-1 alpha-2)
print(user.role_type)      # User role type

# Statistics
print(user.statistics.season.ranked.wins)
print(user.statistics.total.ranked.played_matches)

# Timestamps
print(user.timestamp.first_online)
print(user.timestamp.last_ranked)
```

### Season-Specific Data

```python
# Get data for a specific season
user = mcsrranked.users.get("Feinberg", season=8)
```

## Get User Matches

Retrieve a user's match history:

```python
from mcsrranked import MatchType

# Recent matches
matches = mcsrranked.users.matches("Feinberg")

# With filters
matches = mcsrranked.users.matches(
    "Feinberg",
    count=50,              # Number of matches (1-100)
    sort="newest",         # newest, oldest, fastest, slowest
    type=MatchType.RANKED, # Filter by match type
    season=10,             # Specific season
    excludedecay=True,     # Exclude decay matches
)

# Pagination
matches = mcsrranked.users.matches("Feinberg", before=12345)
```

## Get Season Results

Get a user's results across all seasons:

```python
seasons = mcsrranked.users.seasons("Feinberg")

for season_num, result in seasons.season_results.items():
    print(f"Season {season_num}:")
    print(f"  Final Elo: {result.last.elo_rate}")
    print(f"  Highest: {result.highest}")
    print(f"  Lowest: {result.lowest}")
```

## Versus Statistics

Get head-to-head statistics between two players:

```python
# Get versus stats
stats = mcsrranked.users.versus("Feinberg", "Couriway")

print(f"Ranked results: {stats.results.ranked}")
print(f"Casual results: {stats.results.casual}")
print(f"Elo changes: {stats.changes}")

# Get match history between players
matches = mcsrranked.users.versus_matches("Feinberg", "Couriway", count=20)
```

## Live Match Data

!!! warning "Requires Private Key"
    This endpoint requires a private key generated in-game.

```python
from mcsrranked import MCSRRanked

client = MCSRRanked(private_key="your-private-key")
live = client.users.live("your-uuid")

print(f"Status: {live.status}")
print(f"Time: {live.time}")
print(f"Players: {len(live.players)}")
```
