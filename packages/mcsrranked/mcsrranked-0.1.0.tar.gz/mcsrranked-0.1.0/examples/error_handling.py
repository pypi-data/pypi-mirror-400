"""Error handling examples for the MCSR Ranked SDK."""

import mcsrranked
from mcsrranked import (
    AuthenticationError,
    NotFoundError,
)

# Handle user not found
print("=== Handling NotFoundError ===")
try:
    user = mcsrranked.users.get("this_user_definitely_does_not_exist_12345")
except NotFoundError as e:
    print(f"User not found: {e.message}")
    print(f"Status code: {e.status_code}")
print()

# Handle rate limiting (simulated)
print("=== Handling RateLimitError ===")
print("RateLimitError is raised when you exceed 500 requests per 10 minutes.")
print("Example handling:")
print("""
try:
    for i in range(1000):
        mcsrranked.users.get("Feinberg")
except RateLimitError as e:
    print(f"Rate limited! Wait and retry: {e.message}")
    time.sleep(60)  # Wait before retrying
""")
print()

# Handle authentication errors
print("=== Handling AuthenticationError ===")
print("AuthenticationError is raised when private_key is required but not provided.")
try:
    # This requires a private key
    live = mcsrranked.users.live("some_uuid")
except AuthenticationError as e:
    print(f"Auth error: {e.message}")
print()

# Catch-all error handling
print("=== Catch-all Error Handling ===")
print("Use MCSRRankedError to catch any SDK error:")
print("""
try:
    user = mcsrranked.users.get("someone")
except MCSRRankedError as e:
    print(f"SDK error: {e}")
""")
