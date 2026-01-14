# Exceptions Reference

## Exception Hierarchy

```
MCSRRankedError
├── APIError
│   ├── APIStatusError
│   │   ├── BadRequestError
│   │   ├── AuthenticationError
│   │   ├── NotFoundError
│   │   └── RateLimitError
│   ├── APIConnectionError
│   └── APITimeoutError
```

---

## Base Exceptions

### MCSRRankedError

Base exception for all SDK errors.

```python
from mcsrranked import MCSRRankedError

try:
    user = mcsrranked.users.get("someone")
except MCSRRankedError as e:
    print(f"SDK error: {e}")
```

### APIError

Base exception for API-related errors.

| Attribute | Type | Description |
|-----------|------|-------------|
| `message` | `str` | Error message |

---

## HTTP Status Exceptions

### APIStatusError

Exception for HTTP error responses.

| Attribute | Type | Description |
|-----------|------|-------------|
| `message` | `str` | Error message |
| `status_code` | `int` | HTTP status code |
| `response` | `httpx.Response` | Raw response object |
| `body` | `object \| None` | Response body |

### BadRequestError

Raised for HTTP 400 responses (invalid parameters).

```python
from mcsrranked import BadRequestError

try:
    matches = mcsrranked.matches.list(count=1000)
except BadRequestError as e:
    print(f"Status: {e.status_code}")  # 400
    print(f"Message: {e.message}")
```

### AuthenticationError

Raised for HTTP 401 responses (invalid credentials).

```python
from mcsrranked import AuthenticationError

try:
    live = mcsrranked.users.live("uuid")
except AuthenticationError as e:
    print(f"Status: {e.status_code}")  # 401
```

### NotFoundError

Raised for HTTP 404 responses (resource not found).

```python
from mcsrranked import NotFoundError

try:
    user = mcsrranked.users.get("nonexistent")
except NotFoundError as e:
    print(f"Status: {e.status_code}")  # 404
```

### RateLimitError

Raised for HTTP 429 responses (too many requests).

```python
from mcsrranked import RateLimitError

try:
    # Too many requests
    for i in range(1000):
        mcsrranked.users.get("Feinberg")
except RateLimitError as e:
    print(f"Status: {e.status_code}")  # 429
```

---

## Connection Exceptions

### APIConnectionError

Raised for network-related errors.

```python
from mcsrranked import APIConnectionError

try:
    user = mcsrranked.users.get("Feinberg")
except APIConnectionError as e:
    print(f"Connection failed: {e.message}")
```

### APITimeoutError

Raised when a request times out. Inherits from `APIConnectionError`.

```python
from mcsrranked import APITimeoutError, MCSRRanked

client = MCSRRanked(timeout=1.0)

try:
    user = client.users.get("Feinberg")
except APITimeoutError as e:
    print(f"Request timed out: {e.message}")
```

---

## Import All Exceptions

```python
from mcsrranked import (
    MCSRRankedError,
    APIError,
    APIStatusError,
    APIConnectionError,
    APITimeoutError,
    BadRequestError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
)
```
