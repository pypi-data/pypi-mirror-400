# Leaderboards

The Leaderboards resource provides access to Elo rankings, phase points, and record times.

## Elo Leaderboard

Get the top 150 players by Elo rating:

```python
import mcsrranked

# Current season
leaderboard = mcsrranked.leaderboards.elo()

print(f"Season {leaderboard.season.number}")
print(f"Starts: {leaderboard.season.starts_at}")
print(f"Ends: {leaderboard.season.ends_at}")

for player in leaderboard.users[:10]:
    print(f"#{player.elo_rank} {player.nickname}: {player.elo_rate}")
```

### Filter by Season or Country

```python
# Specific season
leaderboard = mcsrranked.leaderboards.elo(season=8)

# Filter by country (ISO 3166-1 alpha-2, lowercase)
us_leaderboard = mcsrranked.leaderboards.elo(country="us")
uk_leaderboard = mcsrranked.leaderboards.elo(country="gb")
```

## Phase Points Leaderboard

Get the top 100 players by phase points:

```python
phase_lb = mcsrranked.leaderboards.phase()

print(f"Season {phase_lb.phase.season}")
if phase_lb.phase.number:
    print(f"Phase {phase_lb.phase.number}")
    print(f"Ends at: {phase_lb.phase.ends_at}")

for player in phase_lb.users[:10]:
    points = player.season_result.phase_point
    print(f"{player.nickname}: {points} points")
```

### Predicted Phase Points

Get predicted phase points for the next phase:

```python
# Only works with current season
predicted = mcsrranked.leaderboards.phase(predicted=True)

for player in predicted.users[:10]:
    current = player.season_result.phase_point
    predicted = player.pred_phase_point
    print(f"{player.nickname}: {current} -> {predicted} points")
```

## Record Leaderboard

Get the fastest completion times:

```python
# All-time records
records = mcsrranked.leaderboards.record()

# Current season records
records = mcsrranked.leaderboards.record(season=0)

# Specific season records
records = mcsrranked.leaderboards.record(season=8)

for record in records[:10]:
    # Format time as MM:SS.mmm
    minutes = record.time // 60000
    seconds = (record.time % 60000) // 1000
    ms = record.time % 1000
    time_str = f"{minutes}:{seconds:02d}.{ms:03d}"

    print(f"#{record.rank} {record.user.nickname}: {time_str}")
    print(f"  Match ID: {record.id}")
    print(f"  Season: {record.season}")
```

### Distinct Records

Get only the fastest time per player:

```python
# Personal bests only
pb_records = mcsrranked.leaderboards.record(distinct=True)
```

## Leaderboard User Fields

```python
for player in leaderboard.users:
    # Standard user fields
    print(player.uuid)
    print(player.nickname)
    print(player.elo_rate)
    print(player.elo_rank)
    print(player.country)

    # Season result fields
    print(player.season_result.elo_rate)
    print(player.season_result.elo_rank)
    print(player.season_result.phase_point)
```
