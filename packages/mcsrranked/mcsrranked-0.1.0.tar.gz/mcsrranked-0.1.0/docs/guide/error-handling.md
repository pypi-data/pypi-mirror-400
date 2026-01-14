# Error Handling

The SDK provides specific exception types for different error scenarios.

## Exception Hierarchy

```
MCSRRankedError (base)
├── APIError
│   ├── APIStatusError
│   │   ├── BadRequestError (400)
│   │   ├── AuthenticationError (401)
│   │   ├── NotFoundError (404)
│   │   └── RateLimitError (429)
│   ├── APIConnectionError
│   └── APITimeoutError
```

## Common Exceptions

### NotFoundError

Raised when a resource doesn't exist (HTTP 404):

```python
from mcsrranked import NotFoundError

try:
    user = mcsrranked.users.get("nonexistent_user")
except NotFoundError as e:
    print(f"User not found: {e.message}")
    print(f"Status code: {e.status_code}")
```

### RateLimitError

Raised when you exceed the rate limit (HTTP 429):

```python
import time
from mcsrranked import RateLimitError

try:
    # Making too many requests
    for i in range(1000):
        mcsrranked.users.get("Feinberg")
except RateLimitError as e:
    print(f"Rate limited: {e.message}")
    time.sleep(60)  # Wait before retrying
```

!!! info "Rate Limits"
    Default rate limit is 500 requests per 10 minutes.
    Request an API key from [MCSR Ranked Discord](https://mcsrranked.com/discord) for higher limits.

### AuthenticationError

Raised when authentication fails or is missing (HTTP 401):

```python
from mcsrranked import AuthenticationError

try:
    # This requires a private key
    live = mcsrranked.users.live("some_uuid")
except AuthenticationError as e:
    print(f"Auth error: {e.message}")
```

### BadRequestError

Raised for invalid request parameters (HTTP 400):

```python
from mcsrranked import BadRequestError

try:
    # Invalid parameter
    matches = mcsrranked.matches.list(count=1000)  # Max is 100
except BadRequestError as e:
    print(f"Bad request: {e.message}")
```

### APIConnectionError

Raised for network-related errors:

```python
from mcsrranked import APIConnectionError

try:
    user = mcsrranked.users.get("Feinberg")
except APIConnectionError as e:
    print(f"Connection error: {e.message}")
```

### APITimeoutError

Raised when a request times out:

```python
from mcsrranked import APITimeoutError, MCSRRanked

client = MCSRRanked(timeout=5.0)  # 5 second timeout

try:
    user = client.users.get("Feinberg")
except APITimeoutError as e:
    print(f"Request timed out: {e.message}")
```

## Catch-All Error Handling

Use `MCSRRankedError` to catch any SDK error:

```python
from mcsrranked import MCSRRankedError

try:
    user = mcsrranked.users.get("someone")
except MCSRRankedError as e:
    print(f"SDK error: {e}")
```

## APIStatusError Properties

All HTTP error exceptions include additional context:

```python
from mcsrranked import APIStatusError

try:
    user = mcsrranked.users.get("nonexistent")
except APIStatusError as e:
    print(f"Message: {e.message}")
    print(f"Status code: {e.status_code}")
    print(f"Response: {e.response}")
    print(f"Body: {e.body}")
```
