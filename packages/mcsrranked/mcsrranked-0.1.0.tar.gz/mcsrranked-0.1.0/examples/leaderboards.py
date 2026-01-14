"""Leaderboard examples for the MCSR Ranked SDK."""

import mcsrranked

# Elo leaderboard (top 150 players)
print("=== Elo Leaderboard ===")
elo_lb = mcsrranked.leaderboards.elo()
print(f"Season {elo_lb.season.number}")
print(f"Starts: {elo_lb.season.starts_at}")
print(f"Ends: {elo_lb.season.ends_at}")
print()
for player in elo_lb.users[:5]:
    print(f"#{player.elo_rank} {player.nickname}: {player.elo_rate}")
print()

# Elo leaderboard filtered by country
print("=== US Elo Leaderboard ===")
us_lb = mcsrranked.leaderboards.elo(country="us")
for player in us_lb.users[:5]:
    print(f"#{player.elo_rank} {player.nickname}: {player.elo_rate}")
print()

# Phase points leaderboard
print("=== Phase Points Leaderboard ===")
phase_lb = mcsrranked.leaderboards.phase()
if phase_lb.phase.number:
    print(f"Phase {phase_lb.phase.number}")
for player in phase_lb.users[:5]:
    points = player.season_result.phase_point
    print(f"{player.nickname}: {points} points")
print()

# Record leaderboard (best times)
print("=== All-Time Record Leaderboard ===")
records = mcsrranked.leaderboards.record()
for record in records[:5]:
    minutes = record.time // 60000
    seconds = (record.time % 60000) // 1000
    ms = record.time % 1000
    print(f"#{record.rank} {record.user.nickname}: {minutes}:{seconds:02d}.{ms:03d}")
print()

# Record leaderboard - distinct (one per player)
print("=== Personal Best Records ===")
pb_records = mcsrranked.leaderboards.record(distinct=True)
for record in pb_records[:5]:
    minutes = record.time // 60000
    seconds = (record.time % 60000) // 1000
    ms = record.time % 1000
    print(f"#{record.rank} {record.user.nickname}: {minutes}:{seconds:02d}.{ms:03d}")
