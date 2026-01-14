# MCSR Ranked Python SDK

Python SDK for the [MCSR Ranked API](https://mcsrranked.com/).

## Features

- **Type Safety** - Full type hints and Pydantic models
- **Async Support** - Both synchronous and asynchronous clients
- **Modern Tooling** - Built with uv, ruff, and mypy

## Quick Example

```python
import mcsrranked

# Get a player's profile
user = mcsrranked.users.get("Feinberg")
print(f"{user.nickname}: {user.elo_rate} elo")

# Get the leaderboard
leaderboard = mcsrranked.leaderboards.elo()
for player in leaderboard.users[:5]:
    print(f"#{player.elo_rank} {player.nickname}")
```

## Installation

=== "uv"

    ```bash
    uv add mcsrranked
    ```

=== "pip"

    ```bash
    pip install mcsrranked
    ```

## Links

- [GitHub Repository](https://github.com/camodotgg/mcsrranked-python)
- [MCSR Ranked API Documentation](https://mcsrranked.com/api-docs)
- [MCSR Ranked Website](https://mcsrranked.com)
