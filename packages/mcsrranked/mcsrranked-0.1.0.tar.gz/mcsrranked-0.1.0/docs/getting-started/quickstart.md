# Quick Start

This guide will get you up and running with the MCSR Ranked SDK in minutes.

## Basic Usage

The simplest way to use the SDK is through the module-level interface:

```python
import mcsrranked

# Get a user's profile
user = mcsrranked.users.get("Feinberg")
print(f"{user.nickname}: {user.elo_rate} elo (rank #{user.elo_rank})")
```

## Using an Explicit Client

For more control, create a client instance:

```python
from mcsrranked import MCSRRanked

client = MCSRRanked()
user = client.users.get("Feinberg")
```

### Context Manager

Use a context manager to ensure proper cleanup:

```python
from mcsrranked import MCSRRanked

with MCSRRanked() as client:
    user = client.users.get("Feinberg")
    matches = client.users.matches(user.uuid)
```

## Common Operations

### Get User Profile

```python
user = mcsrranked.users.get("Feinberg")
print(f"UUID: {user.uuid}")
print(f"Nickname: {user.nickname}")
print(f"Elo: {user.elo_rate}")
print(f"Rank: #{user.elo_rank}")
```

### Get Recent Matches

```python
matches = mcsrranked.matches.list(count=10)
for match in matches:
    print(f"Match {match.id}: {len(match.players)} players")
```

### Get Leaderboard

```python
leaderboard = mcsrranked.leaderboards.elo()
for player in leaderboard.users[:10]:
    print(f"#{player.elo_rank} {player.nickname}: {player.elo_rate}")
```

### Get Live Data

```python
live = mcsrranked.live.get()
print(f"Online players: {live.players}")
print(f"Live matches: {len(live.live_matches)}")
```

## Next Steps

- Learn about [Users](../guide/users.md) in detail
- Explore [Leaderboards](../guide/leaderboards.md)
- Set up [Async Usage](../guide/async.md) for better performance
- Handle [Errors](../guide/error-handling.md) gracefully
