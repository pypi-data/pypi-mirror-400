#!/usr/bin/env python3
"""Find trending products in a topic.

Usage:
    1. Create examples/.env with: PRODUCTHUNT_TOKEN=your_token
    2. Run: uv run python examples/find_trends.py [topic] [days]
"""

import os
import sys
from datetime import UTC, datetime, timedelta

from dotenv import load_dotenv

from producthunt_sdk import BearerAuth, PostsOrder, ProductHuntClient

load_dotenv()


def main(topic: str = "artificial-intelligence", days: int = 7):
    client = ProductHuntClient(auth=BearerAuth(os.getenv("PRODUCTHUNT_TOKEN", "")))

    posts = client.get_posts(
        topic=topic,
        posted_after=datetime.now(UTC) - timedelta(days=days),
        order=PostsOrder.VOTES,
        first=10,
    )

    print(f"\nTop products in '{topic}' (last {days} days)\n")

    for i, post in enumerate(posts.nodes, 1):
        print(f"  {i}. {post.name} ({post.votes_count} votes)")
        print(f"     {post.tagline}\n")


if __name__ == "__main__":
    topic = sys.argv[1] if len(sys.argv) > 1 else "artificial-intelligence"
    days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    main(topic, days)
