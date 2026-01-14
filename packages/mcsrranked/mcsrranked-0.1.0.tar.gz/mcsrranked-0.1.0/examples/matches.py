"""Match examples for the MCSR Ranked SDK."""

import mcsrranked
from mcsrranked import MatchType


def format_time(ms: int) -> str:
    """Format milliseconds as MM:SS.mmm."""
    minutes = ms // 60000
    seconds = (ms % 60000) // 1000
    millis = ms % 1000
    return f"{minutes}:{seconds:02d}.{millis:03d}"


# Get recent matches
print("=== Recent Matches ===")
matches = mcsrranked.matches.list(count=5)
for match in matches:
    match_type = MatchType(match.type).name
    players = ", ".join(p.nickname for p in match.players)
    time_str = format_time(match.result.time) if match.result else "N/A"
    print(f"Match {match.id} ({match_type}): {players} - {time_str}")
print()

# Get ranked matches only
print("=== Recent Ranked Matches ===")
ranked = mcsrranked.matches.list(type=MatchType.RANKED, count=5)
for match in ranked:
    players = " vs ".join(p.nickname for p in match.players)
    winner = next(
        (
            p.nickname
            for p in match.players
            if match.result and p.uuid == match.result.uuid
        ),
        "Draw",
    )
    print(f"Match {match.id}: {players} - Winner: {winner}")
print()

# Get detailed match info
print("=== Detailed Match Info ===")
match = mcsrranked.matches.get(ranked[0].id)
print(f"Match ID: {match.id}")
print(f"Season: {match.season}")
print(f"Type: {MatchType(match.type).name}")
print(f"Date: {match.date}")
print()

print("Players:")
for player in match.players:
    print(f"  {player.nickname} ({player.uuid})")
print()

print("Elo Changes:")
for change in match.changes:
    player = next((p for p in match.players if p.uuid == change.uuid), None)
    name = player.nickname if player else change.uuid
    change_str = (
        f"+{change.change}"
        if change.change and change.change > 0
        else str(change.change)
    )
    print(f"  {name}: {change_str} (now {change.elo_rate})")
print()

if match.timelines:
    print("Timeline:")
    for event in match.timelines[:10]:
        player = next((p for p in match.players if p.uuid == event.uuid), None)
        name = player.nickname if player else event.uuid[:8]
        print(f"  {format_time(event.time)} - {name}: {event.type}")
