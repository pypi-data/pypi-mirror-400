# Installation

## Requirements

- Python 3.11 or higher

## Install with uv

```bash
uv add mcsrranked
```

## Install with pip

```bash
pip install mcsrranked
```

## Verify Installation

```python
import mcsrranked
print(mcsrranked.__version__)
```

## Optional: API Key

By default, the API has a rate limit of 500 requests per 10 minutes. If you need higher limits, you can request an API key from the [MCSR Ranked Discord](https://mcsrranked.com/discord).

Set your API key via environment variable:

```bash
export MCSRRANKED_API_KEY="your-api-key"
```

Or pass it directly to the client:

```python
from mcsrranked import MCSRRanked

client = MCSRRanked(api_key="your-api-key")
```
