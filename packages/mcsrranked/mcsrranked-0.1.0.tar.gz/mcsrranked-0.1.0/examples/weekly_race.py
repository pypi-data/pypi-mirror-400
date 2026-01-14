"""Weekly race examples for the MCSR Ranked SDK."""

import mcsrranked


def format_time(ms: int) -> str:
    """Format milliseconds as MM:SS.mmm."""
    minutes = ms // 60000
    seconds = (ms % 60000) // 1000
    millis = ms % 1000
    return f"{minutes}:{seconds:02d}.{millis:03d}"


# Get current weekly race
print("=== Current Weekly Race ===")
race = mcsrranked.weekly_races.get()
print(f"Race ID: {race.id}")
print(f"Ends at: {race.ends_at}")
print()

print("Seed Info:")
if race.seed.overworld:
    print(f"  Overworld: {race.seed.overworld}")
if race.seed.nether:
    print(f"  Nether: {race.seed.nether}")
if race.seed.the_end:
    print(f"  The End: {race.seed.the_end}")
print()

print("Top 10 Leaderboard:")
for entry in race.leaderboard[:10]:
    time_str = format_time(entry.time)
    replay = " [replay]" if entry.replay_exist else ""
    print(f"  #{entry.rank} {entry.player.nickname}: {time_str}{replay}")
print()

# Get a specific past weekly race
print("=== Past Weekly Race (ID 1) ===")
past_race = mcsrranked.weekly_races.get(race_id=1)
print(f"Race ID: {past_race.id}")
print(f"Winner: {past_race.leaderboard[0].player.nickname}")
print(f"Winning time: {format_time(past_race.leaderboard[0].time)}")
