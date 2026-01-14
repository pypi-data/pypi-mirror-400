"""Async usage examples for the MCSR Ranked SDK."""

import asyncio

from mcsrranked import AsyncMCSRRanked


async def main() -> None:
    """Demonstrate async SDK usage."""
    async with AsyncMCSRRanked() as client:
        # Fetch multiple users concurrently
        users = await asyncio.gather(
            client.users.get("Feinberg"),
            client.users.get("k4yfour"),
            client.users.get("Couriway"),
        )

        print("Players fetched concurrently:")
        for user in users:
            elo = user.elo_rate or "Unranked"
            print(f"  {user.nickname}: {elo}")
        print()

        # Fetch leaderboard and live data concurrently
        leaderboard, live = await asyncio.gather(
            client.leaderboards.elo(),
            client.live.get(),
        )

        print(
            f"Season {leaderboard.season.number} leader: {leaderboard.users[0].nickname}"
        )
        print(f"Online players: {live.players}")
        print(f"Live matches: {len(live.live_matches)}")


if __name__ == "__main__":
    asyncio.run(main())
