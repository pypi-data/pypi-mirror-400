# Async Usage

The SDK provides a fully async client for use with `asyncio`.

## Basic Async Usage

```python
import asyncio
from mcsrranked import AsyncMCSRRanked

async def main():
    async with AsyncMCSRRanked() as client:
        user = await client.users.get("Feinberg")
        print(f"{user.nickname}: {user.elo_rate} elo")

asyncio.run(main())
```

## Context Manager

Always use the async context manager to ensure proper cleanup:

```python
async with AsyncMCSRRanked() as client:
    # Use client here
    pass
# Client is automatically closed
```

Or manually close the client:

```python
client = AsyncMCSRRanked()
try:
    user = await client.users.get("Feinberg")
finally:
    await client.close()
```

## Concurrent Requests

Use `asyncio.gather()` to make multiple requests concurrently:

```python
import asyncio
from mcsrranked import AsyncMCSRRanked

async def main():
    async with AsyncMCSRRanked() as client:
        # Fetch multiple users concurrently
        users = await asyncio.gather(
            client.users.get("Feinberg"),
            client.users.get("Couriway"),
            client.users.get("k4yfour"),
        )

        for user in users:
            print(f"{user.nickname}: {user.elo_rate}")

asyncio.run(main())
```

## Real-World Example

Fetch a user and their recent matches concurrently:

```python
import asyncio
from mcsrranked import AsyncMCSRRanked

async def get_user_with_matches(client, identifier):
    """Fetch user and their matches concurrently."""
    user, matches = await asyncio.gather(
        client.users.get(identifier),
        client.users.matches(identifier, count=10),
    )
    return user, matches

async def main():
    async with AsyncMCSRRanked() as client:
        user, matches = await get_user_with_matches(client, "Feinberg")

        print(f"{user.nickname} ({user.elo_rate} elo)")
        print(f"Recent matches: {len(matches)}")

        wins = sum(1 for m in matches if m.result and m.result.uuid == user.uuid)
        print(f"Wins: {wins}/{len(matches)}")

asyncio.run(main())
```

## Async with Error Handling

```python
import asyncio
from mcsrranked import AsyncMCSRRanked, NotFoundError, RateLimitError

async def safe_get_user(client, identifier):
    """Safely fetch a user with error handling."""
    try:
        return await client.users.get(identifier)
    except NotFoundError:
        print(f"User {identifier} not found")
        return None
    except RateLimitError:
        print("Rate limited, waiting...")
        await asyncio.sleep(60)
        return await safe_get_user(client, identifier)

async def main():
    async with AsyncMCSRRanked() as client:
        user = await safe_get_user(client, "Feinberg")
        if user:
            print(f"Found: {user.nickname}")

asyncio.run(main())
```

## Client Configuration

The async client accepts the same options as the sync client:

```python
client = AsyncMCSRRanked(
    api_key="your-api-key",
    private_key="your-private-key",
    timeout=60.0,
    max_retries=3,
)
```

## Comparison: Sync vs Async

| Sync | Async |
|------|-------|
| `MCSRRanked()` | `AsyncMCSRRanked()` |
| `client.users.get()` | `await client.users.get()` |
| `with client:` | `async with client:` |
| `client.close()` | `await client.close()` |

Both clients have identical APIs - the only difference is adding `await` before method calls and using `async with` for context managers.
