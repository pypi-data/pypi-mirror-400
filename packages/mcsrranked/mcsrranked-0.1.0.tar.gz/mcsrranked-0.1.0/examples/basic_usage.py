"""Basic usage examples for the MCSR Ranked SDK."""

import mcsrranked

# Get a user's profile
user = mcsrranked.users.get("Feinberg")
print(f"Player: {user.nickname}")
print(f"Elo: {user.elo_rate}")
print(f"Rank: #{user.elo_rank}")
print(f"Country: {user.country}")
print()

# Get user's recent matches
matches = mcsrranked.users.matches(user.uuid, count=5)
print(f"Recent matches for {user.nickname}:")
for match in matches:
    winner = "Win" if match.result and match.result.uuid == user.uuid else "Loss"
    time_str = f"{match.result.time}ms" if match.result else "N/A"
    print(f"  Match {match.id}: {winner} - {time_str}")
print()

# Get the elo leaderboard
leaderboard = mcsrranked.leaderboards.elo()
print(f"Season {leaderboard.season.number} Top 10:")
for player in leaderboard.users[:10]:
    print(f"  #{player.elo_rank} {player.nickname}: {player.elo_rate}")
