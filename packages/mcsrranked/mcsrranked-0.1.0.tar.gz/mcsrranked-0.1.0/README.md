# mcsrranked

mcsrranked is a Python SDK for the [MCSR Ranked API](https://mcsrranked.com/).

[![PyPI version](https://badge.fury.io/py/mcsrranked.svg)](https://badge.fury.io/py/mcsrranked)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
# Using uv
uv add mcsrranked

# Using pip
pip install mcsrranked
```

## Examples

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

See more [examples](https://github.com/camodotgg/mcsrranked-python/tree/main/examples).

## Documentation

For full documentation, visit **[camodotgg.github.io/mcsrranked-python](https://camodotgg.github.io/mcsrranked-python)**.

- [Getting Started](https://camodotgg.github.io/mcsrranked-python/getting-started/quickstart/)
- [API Reference](https://camodotgg.github.io/mcsrranked-python/api/client/)
- [Examples](https://camodotgg.github.io/mcsrranked-python/examples/)

## Contributing

```bash
git clone https://github.com/camodotgg/mcsrranked-python
cd mcsrranked-python
uv sync --all-extras
uv run pre-commit install
```

Run checks:

```bash
uv run ruff check src/
uv run mypy src/
uv run pytest
```
