# ethos-py

**The unofficial Python SDK for [Ethos Network](https://ethos.network) API**

First Python client for interacting with Ethos Network's on-chain reputation protocol.

[![PyPI version](https://badge.fury.io/py/ethos-py.svg)](https://badge.fury.io/py/ethos-py)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Installation

```bash
pip install ethos-py
```

---

## Quick Start

```python
from ethos import Ethos

# Initialize client
client = Ethos()

# Get a profile by Twitter handle
profile = client.profiles.get_by_twitter("vitalikbuterin")
print(f"{profile.twitter_handle}: {profile.credibility_score}")

# List all vouches
for vouch in client.vouches.list():
    print(f"{vouch.author_profile_id} vouched for {vouch.target_profile_id}")

# Get vouches for a specific profile
vouches = client.vouches.list(target_profile_id=123)

# Search users
users = client.profiles.search("ethereum")
```

---

## Features

- **Simple, Pythonic API** - Resource-based design (`client.vouches.list()`)
- **Type hints everywhere** - Full autocomplete and mypy support
- **Pydantic models** - Validated, typed response objects
- **Auto-pagination** - Iterate through all results seamlessly
- **Built-in rate limiting** - Respects API limits automatically
- **Retry with backoff** - Handles transient failures gracefully
- **Async support** - `async/await` ready for high-performance apps

---

## Usage

### Profiles

```python
from ethos import Ethos

client = Ethos()

# Get profile by ID
profile = client.profiles.get(123)

# Get profile by Ethereum address
profile = client.profiles.get_by_address("0x123...")

# Get profile by Twitter handle
profile = client.profiles.get_by_twitter("username")

# Search profiles
profiles = client.profiles.search("query", limit=20)

# List all profiles (auto-paginated)
for profile in client.profiles.list():
    print(profile.credibility_score)
```

### Vouches

```python
# List all vouches
vouches = client.vouches.list()

# Filter vouches
vouches = client.vouches.list(
    target_profile_id=123,      # Vouches received by profile
    author_profile_id=456,      # Vouches given by profile
)

# Iterate through all vouches (auto-pagination)
for vouch in client.vouches.list():
    print(f"Amount: {vouch.amount_wei} wei")
```

### Reviews

```python
# List all reviews
reviews = client.reviews.list()

# Filter by target
reviews = client.reviews.list(target_profile_id=123)

# Filter by sentiment
positive_reviews = client.reviews.list(score="positive")
negative_reviews = client.reviews.list(score="negative")
```

### Markets (Reputation Trading)

```python
# List reputation markets
markets = client.markets.list()

# Get specific market
market = client.markets.get(market_id=1)

print(f"Trust price: {market.trust_price}")
print(f"Distrust price: {market.distrust_price}")
```

### Activities

```python
# List all activities
activities = client.activities.list()

# Filter by type
vouch_activities = client.activities.list(activity_type="vouch")
review_activities = client.activities.list(activity_type="review")
```

### Credibility Scores

```python
# Get score for an address
score = client.scores.get("0x123...")
print(f"Score: {score.value}")
print(f"Level: {score.level}")  # "untrusted", "neutral", "trusted", etc.
```

---

## Async Support

```python
import asyncio
from ethos import AsyncEthos

async def main():
    async with AsyncEthos() as client:
        profile = await client.profiles.get(123)
        vouches = await client.vouches.list(target_profile_id=123)
        
asyncio.run(main())
```

---

## Configuration

### Environment Variables

```bash
# Optional: Custom client name (for rate limit tracking)
export ETHOS_CLIENT_NAME="my-app"

# Optional: Custom base URL
export ETHOS_API_BASE_URL="https://api.ethos.network/api/v2"
```

### Client Options

```python
from ethos import Ethos

client = Ethos(
    client_name="my-app",           # Identifies your app to Ethos
    rate_limit=0.5,                 # Seconds between requests
    timeout=30,                     # Request timeout
    max_retries=3,                  # Retry failed requests
)
```

---

## Response Models

All responses are Pydantic models with full type hints:

```python
from ethos.types import Profile, Vouch, Review

profile: Profile = client.profiles.get(123)

# Access typed attributes
profile.id                    # int
profile.address               # str
profile.twitter_handle        # Optional[str]
profile.credibility_score     # int
profile.score_level           # str
profile.created_at            # datetime

# Convert to dict
profile.model_dump()

# Convert to JSON
profile.model_dump_json()
```

---

## Error Handling

```python
from ethos import Ethos
from ethos.exceptions import (
    EthosAPIError,
    EthosNotFoundError,
    EthosRateLimitError,
    EthosValidationError,
)

client = Ethos()

try:
    profile = client.profiles.get(999999)
except EthosNotFoundError:
    print("Profile not found")
except EthosRateLimitError:
    print("Rate limited - slow down")
except EthosAPIError as e:
    print(f"API error: {e.status_code} - {e.message}")
```

---

## Pagination

The SDK handles pagination automatically:

```python
# This iterates through ALL vouches, fetching pages as needed
for vouch in client.vouches.list():
    process(vouch)

# Or get a specific page
page = client.vouches.list(limit=100, offset=200)
```

---

## Development

```bash
# Clone the repo
git clone https://github.com/kluless13/ethos-python-sdk.git
cd ethos-python-sdk

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy src/ethos

# Formatting
black src tests
ruff check src tests
```

---

## Why This Exists

Ethos Network provides a REST API but no official Python SDK. This library fills that gap for:

- **Researchers** analyzing on-chain reputation data
- **Data scientists** building trust metrics
- **Developers** integrating Ethos into Python applications
- **Analysts** studying Web3 social dynamics

---

## Related Projects

- [Ethos Network](https://ethos.network) - The protocol
- [Ethos API Docs](https://developers.ethos.network) - Official API documentation
- [ethos-research](https://github.com/kluless13/ethos-research) - Research using this SDK

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

---

## Disclaimer

This is an unofficial SDK and is not affiliated with or endorsed by Ethos Network.
