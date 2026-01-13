# Examples

## Setup

1. Copy `.env.example` to `.env`
2. Add your token from [producthunt.com/v2/oauth/applications](https://www.producthunt.com/v2/oauth/applications)

```bash
cp .env.example .env
# Edit .env and add your token
```

## Data Access Note

Product Hunt's API has privacy restrictions:
- **Public data** (posts, topics, collections): Full access
- **Your own data** (profile, posts, votes, followers): Full access
- **Other users' data**: Redacted for privacy

## Examples

### Quickstart

```bash
uv run python examples/quickstart.py
```

### View Your Profile

```bash
uv run python examples/my_profile.py
```

### Track a Product Launch

```bash
uv run python examples/track_launch.py chatgpt
```

### Find Trending Products

```bash
uv run python examples/find_trends.py artificial-intelligence 7
```

### Analyze Product Engagement

```bash
uv run python examples/analyze_competitors.py chatgpt
```

### OAuth Flow

For apps that authenticate users:

```bash
# Start ngrok first: ngrok http 8000
uv run python examples/oauth_flow.py
```

## Test All Endpoints

Run all SDK methods to validate everything works (requires OAuth):

```bash
# Start ngrok first: ngrok http 8000
uv run python examples/test_all_endpoints.py
```
