"""Versus (head-to-head) examples for the MCSR Ranked SDK."""

import mcsrranked


def format_time(ms: int) -> str:
    """Format milliseconds as MM:SS.mmm."""
    minutes = ms // 60000
    seconds = (ms % 60000) // 1000
    millis = ms % 1000
    return f"{minutes}:{seconds:02d}.{millis:03d}"


# Get versus stats between two players
player1 = "Feinberg"
player2 = "k4yfour"

print(f"=== {player1} vs {player2} ===")
stats = mcsrranked.users.versus(player1, player2)

# Display players
for player in stats.players:
    elo = player.elo_rate or "Unranked"
    print(f"{player.nickname}: {elo} elo")
print()

# Display ranked results
print("Ranked Results:")
ranked = stats.results.ranked
total = ranked.get("total", 0)
for uuid, wins in ranked.items():
    if uuid != "total":
        player = next((p for p in stats.players if p.uuid == uuid), None)
        name = player.nickname if player else uuid[:8]
        print(f"  {name}: {wins} wins")
print(f"  Total matches: {total}")
print()

# Display casual results
print("Casual Results:")
casual = stats.results.casual
total = casual.get("total", 0)
for uuid, wins in casual.items():
    if uuid != "total":
        player = next((p for p in stats.players if p.uuid == uuid), None)
        name = player.nickname if player else uuid[:8]
        print(f"  {name}: {wins} wins")
print(f"  Total matches: {total}")
print()

# Display elo changes
print("Total Elo Changes:")
for uuid, change in stats.changes.items():
    player = next((p for p in stats.players if p.uuid == uuid), None)
    name = player.nickname if player else uuid[:8]
    sign = "+" if change > 0 else ""
    print(f"  {name}: {sign}{change}")
print()

# Get match history between the two players
print(f"=== Recent Matches Between {player1} and {player2} ===")
matches = mcsrranked.users.versus_matches(player1, player2, count=5)
for match in matches:
    winner = next(
        (
            p.nickname
            for p in match.players
            if match.result and p.uuid == match.result.uuid
        ),
        "Draw",
    )
    time_str = format_time(match.result.time) if match.result else "N/A"
    print(f"Match {match.id}: Winner: {winner} - {time_str}")
