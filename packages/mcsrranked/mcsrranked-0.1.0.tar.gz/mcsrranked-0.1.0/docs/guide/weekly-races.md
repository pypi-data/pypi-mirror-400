# Weekly Races

The Weekly Races resource provides access to weekly race information and leaderboards.

## Get Current Weekly Race

```python
import mcsrranked

race = mcsrranked.weekly_races.get()

print(f"Race ID: {race.id}")
print(f"Ends at: {race.ends_at}")  # Unix timestamp
```

## Seed Information

```python
print("Seed Info:")
if race.seed.overworld:
    print(f"  Overworld: {race.seed.overworld}")
if race.seed.nether:
    print(f"  Nether: {race.seed.nether}")
if race.seed.the_end:
    print(f"  The End: {race.seed.the_end}")
if race.seed.rng:
    print(f"  RNG: {race.seed.rng}")
```

## Leaderboard

```python
def format_time(ms: int) -> str:
    """Format milliseconds as MM:SS.mmm."""
    minutes = ms // 60000
    seconds = (ms % 60000) // 1000
    millis = ms % 1000
    return f"{minutes}:{seconds:02d}.{millis:03d}"

for entry in race.leaderboard[:10]:
    time_str = format_time(entry.time)
    replay = " [replay]" if entry.replay_exist else ""
    print(f"#{entry.rank} {entry.player.nickname}: {time_str}{replay}")
```

## Get Past Weekly Race

```python
# Get a specific week by ID
past_race = mcsrranked.weekly_races.get(race_id=1)

print(f"Race ID: {past_race.id}")
print(f"Winner: {past_race.leaderboard[0].player.nickname}")
```

## Leaderboard Entry Fields

```python
for entry in race.leaderboard:
    print(entry.rank)         # Position in leaderboard
    print(entry.time)         # Completion time in ms
    print(entry.replay_exist) # Whether replay is available

    # Player info
    print(entry.player.uuid)
    print(entry.player.nickname)
    print(entry.player.elo_rate)
```
