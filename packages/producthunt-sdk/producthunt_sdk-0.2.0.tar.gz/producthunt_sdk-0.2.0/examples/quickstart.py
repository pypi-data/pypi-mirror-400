#!/usr/bin/env python3
"""Quickstart example for Product Hunt SDK.

Usage:
    1. Create examples/.env with: PRODUCTHUNT_TOKEN=your_token
    2. Run: uv run python examples/quickstart.py
"""

import os

from dotenv import load_dotenv

from producthunt_sdk import BearerAuth, ProductHuntClient

load_dotenv()

token = os.getenv("PRODUCTHUNT_TOKEN", "")
client = ProductHuntClient(auth=BearerAuth(token))

# Get today's featured products
posts = client.get_posts(featured=True, first=5)

print("Today's Top Products on Product Hunt:\n")
for i, post in enumerate(posts.nodes, 1):
    print(f"{i}. {post.name} ({post.votes_count} votes)")
    print(f"   {post.tagline}\n")
