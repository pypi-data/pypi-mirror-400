# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python SDK for the Product Hunt API v2 (GraphQL). Provides both sync and async clients with automatic rate limiting, retries, and Pydantic models.

**Authentication**: Three options:
- Developer Token (simple): `BearerAuth("token")` - Get at https://www.producthunt.com/v2/oauth/applications
- Client Credentials (server-side): `ClientCredentials(client_id, client_secret)` - No browser, public data only
- OAuth (user auth): `OAuth2(client_id, client_secret)` - Auto handles browser flow, token caching

**Data Access**: Product Hunt API has privacy restrictions - other users' data is redacted. Only your own profile data is fully accessible.

## Development Setup

```bash
# Install dependencies
uv sync --all-extras

# Run examples (create examples/.env with PRODUCTHUNT_TOKEN=your_token)
uv run python examples/track_launch.py chatgpt
uv run python examples/test_all_endpoints.py
```

## Commands

```bash
# Linting
uv run ruff check
uv run ruff check --fix

# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v
```

## Architecture

```
producthunt_sdk/
    ├── __init__.py      # Public API exports
    ├── client.py        # ProductHuntClient and AsyncProductHuntClient
    ├── models.py        # Pydantic models for GraphQL types
    ├── queries.py       # GraphQL query/mutation strings with fragments
    ├── rate_limiter.py  # Rate limit handling with auto-wait
    ├── auth.py          # BearerAuth, ClientCredentials, OAuth2, TokenCache
    └── exceptions.py    # Custom exceptions (all inherit ProductHuntError)

examples/
    ├── .env                        # Token storage (gitignored)
    ├── .env.example                # Template for .env
    ├── track_launch.py             # Track your launch performance
    ├── find_trends.py              # Find trending products
    ├── analyze_competitors.py      # Analyze competitor engagement
    ├── my_profile.py               # View your own profile data
    ├── oauth_flow.py               # OAuth flow demo
    ├── test_client_credentials.py  # Test ClientCredentials auth
    └── test_all_endpoints.py       # Manual test of all SDK methods

tests/
    ├── conftest.py          # Fixtures, mock transports, sample data
    ├── test_client.py       # Sync client tests
    ├── test_async_client.py # Async client tests
    ├── test_auth.py         # Auth classes tests (BearerAuth, ClientCredentials, OAuth2)
    ├── test_models.py       # Pydantic model tests
    └── test_rate_limiter.py # Rate limiter tests
```

## Key Components

### Authentication (`auth.py`)

```python
# Developer token (simple)
from producthunt_sdk import ProductHuntClient, BearerAuth
client = ProductHuntClient(auth=BearerAuth("your_token"))

# Client credentials (server-side, no browser, public data only)
from producthunt_sdk import ProductHuntClient, ClientCredentials
client = ProductHuntClient(auth=ClientCredentials(
    client_id="...",
    client_secret="...",
))
# Token fetched automatically on first request, cached for reuse

# OAuth (auto browser flow, token caching, user-level access)
from producthunt_sdk import ProductHuntClient, OAuth2
client = ProductHuntClient(auth=OAuth2(
    client_id="...",
    client_secret="...",
    redirect_uri="https://your-ngrok.ngrok.io/callback",  # Optional
))
# First API call opens browser, handles callback, caches token

# File-based token persistence
from producthunt_sdk import OAuth2, ClientCredentials, TokenCache
OAuth2.token_cache = TokenCache("~/.producthunt_tokens.json")
ClientCredentials.token_cache = TokenCache("~/.producthunt_tokens.json")
```

### Client (`client.py`)

Two client classes with identical method signatures:
- `ProductHuntClient` - synchronous, uses `httpx.Client`
- `AsyncProductHuntClient` - asynchronous, uses `httpx.AsyncClient`

Features:
- Context manager support for automatic cleanup
- Automatic retries via tenacity (network errors, 5xx, 429)
- Rate limit tracking and auto-wait
- Public `graphql()` method for custom queries

### Rate Limiter (`rate_limiter.py`)

Tracks `X-Rate-Limit-*` headers from responses. When `auto_wait=True` (default), automatically sleeps when rate limited.

API limits:
- GraphQL: 6,250 complexity points per 15 minutes
- Request-based: 450 requests per 15 minutes

### Models (`models.py`)

Pydantic v2 models with camelCase aliases. Key types:
- `Post`, `User`, `Topic`, `Collection`, `Comment`, `Vote`
- Connection types (`PostConnection`, etc.) with `.nodes` property
- Order enums: `PostsOrder`, `CollectionsOrder`, `CommentsOrder`, `TopicsOrder`

### Exceptions (`exceptions.py`)

All inherit from `ProductHuntError`:
- `AuthenticationError` - invalid/expired token
- `GraphQLError` - API returned errors
- `MutationError` - mutation-specific errors
- `RateLimitError` - rate limit exceeded (when auto_wait=False)

## Available API Methods

### Queries
- `get_post(id, slug)` / `get_posts(...)` - posts with filtering
- `get_user(id, username)` - user profiles (your own data only)
- `get_user_posts(...)` / `get_user_voted_posts(...)` - user's posts
- `get_user_followers(...)` / `get_user_following(...)` - user relationships
- `get_topic(id, slug)` / `get_topics(...)` - topics/categories
- `get_collection(id, slug)` / `get_collections(...)` - curated collections
- `get_collection_posts(...)` - posts in a collection
- `get_post_comments(...)` / `get_post_votes(...)` - post engagement
- `get_comment(id)` - single comment
- `get_viewer()` - authenticated user context

### Mutations
- `follow_user(user_id)` / `unfollow_user(user_id)`

## Pagination Pattern

All list endpoints use cursor-based pagination:
```python
posts = client.get_posts(first=20)
if posts.page_info.has_next_page:
    more = client.get_posts(first=20, after=posts.page_info.end_cursor)
```

## Dependencies

Core: `httpx`, `pydantic`, `tenacity`
Dev: `pytest`, `pytest-asyncio`, `ruff`
Examples: `python-dotenv`
