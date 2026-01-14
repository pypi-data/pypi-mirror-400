# Live Data

The Live resource provides access to online player counts and live streaming matches.

## Get Live Data

```python
import mcsrranked

live = mcsrranked.live.get()

print(f"Online players: {live.players}")
print(f"Live matches: {len(live.live_matches)}")
```

## Live Matches

Live matches are only included if at least one player has public streaming enabled.

```python
for match in live.live_matches:
    print(f"Current time: {match.current_time}ms")

    # Players with public streams
    for player in match.players:
        print(f"  {player.nickname}")

    # Player data (includes stream URLs and timelines)
    for uuid, data in match.data.items():
        if data.live_url:
            print(f"  Stream: {data.live_url}")
        if data.timeline:
            print(f"  Last split: {data.timeline.type} at {data.timeline.time}ms")
```

## Enabling Public Streams

To have your matches appear in live data:

1. Link your Twitch account to your MCSR Ranked profile
2. Make Twitch public on your MCSR Ranked profile
3. Enable "Public Stream" in MCSR Ranked settings
4. Start streaming on Twitch

## User Live Match

!!! warning "Requires Private Key"
    This endpoint requires a private key generated in-game:
    Profile → Settings → Generate & Copy API Private Key

Get live match data for a specific user in a private room:

```python
from mcsrranked import MCSRRanked

# Set private key via environment variable
# export MCSRRANKED_PRIVATE_KEY="your-key"

client = MCSRRanked(private_key="your-key")
live = client.users.live("your-uuid")

print(f"Status: {live.status}")  # idle, counting, generate, ready, running, done
print(f"Match type: {live.type}")
print(f"Time: {live.time}ms")
print(f"Last match ID: {live.last_id}")

# Players and spectators
print(f"Players: {len(live.players)}")
print(f"Spectators: {len(live.spectators)}")

# Timeline events
for event in live.timelines:
    print(f"{event.time}ms - {event.uuid}: {event.type}")

# Completions
for completion in live.completions:
    print(f"{completion.uuid} finished at {completion.time}ms")
```

The user must be the host or co-host of the private room to access this data.
