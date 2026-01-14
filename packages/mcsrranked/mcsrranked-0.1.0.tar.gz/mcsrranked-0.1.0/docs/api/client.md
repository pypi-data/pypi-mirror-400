# Client Reference

## MCSRRanked

The synchronous client for the MCSR Ranked API.

```python
from mcsrranked import MCSRRanked

client = MCSRRanked(
    api_key=None,        # API key for expanded rate limits
    private_key=None,    # Private key for live data
    base_url=None,       # Custom API base URL
    timeout=30.0,        # Request timeout in seconds
    max_retries=2,       # Maximum retry attempts
)
```

### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | `str \| None` | `None` | API key for expanded rate limits. Falls back to `MCSRRANKED_API_KEY` env var. |
| `private_key` | `str \| None` | `None` | Private key for live data. Falls back to `MCSRRANKED_PRIVATE_KEY` env var. |
| `base_url` | `str \| None` | `"https://api.mcsrranked.com"` | API base URL. |
| `timeout` | `float \| None` | `30.0` | Request timeout in seconds. |
| `max_retries` | `int \| None` | `2` | Maximum number of retries. |

### Resources

| Resource | Description |
|----------|-------------|
| `client.users` | User profiles, matches, versus stats |
| `client.matches` | Match listings and details |
| `client.leaderboards` | Elo, phase, and record leaderboards |
| `client.live` | Online players and live streams |
| `client.weekly_races` | Weekly race data |

### Methods

#### `with_options(**kwargs)`

Create a new client with modified options:

```python
new_client = client.with_options(timeout=60.0)
```

#### `close()`

Close the HTTP client:

```python
client.close()
```

### Context Manager

```python
with MCSRRanked() as client:
    user = client.users.get("Feinberg")
# Client automatically closed
```

---

## AsyncMCSRRanked

The asynchronous client for the MCSR Ranked API.

```python
from mcsrranked import AsyncMCSRRanked

client = AsyncMCSRRanked(
    api_key=None,
    private_key=None,
    base_url=None,
    timeout=30.0,
    max_retries=2,
)
```

### Async Context Manager

```python
async with AsyncMCSRRanked() as client:
    user = await client.users.get("Feinberg")
# Client automatically closed
```

### Async Methods

All resource methods are async:

```python
user = await client.users.get("Feinberg")
matches = await client.matches.list()
leaderboard = await client.leaderboards.elo()
```

### Async Close

```python
await client.close()
```

---

## Module-Level Access

The SDK provides module-level access without creating a client:

```python
import mcsrranked

user = mcsrranked.users.get("Feinberg")
matches = mcsrranked.matches.list()
```

!!! note
    Module-level access uses a lazily-created internal client. For async usage, you must use `AsyncMCSRRanked` explicitly.
