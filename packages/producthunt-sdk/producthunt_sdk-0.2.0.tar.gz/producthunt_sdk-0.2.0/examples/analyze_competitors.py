#!/usr/bin/env python3
"""Analyze product engagement on Product Hunt.

Usage:
    1. Create examples/.env with: PRODUCTHUNT_TOKEN=your_token
    2. Run: uv run python examples/analyze_competitors.py product-slug
"""

import os
import sys

from dotenv import load_dotenv

from producthunt_sdk import BearerAuth, CommentsOrder, ProductHuntClient

load_dotenv()


def main(slug: str):
    client = ProductHuntClient(auth=BearerAuth(os.getenv("PRODUCTHUNT_TOKEN", "")))

    post = client.get_post(slug=slug)
    if not post:
        print(f"Product '{slug}' not found")
        return

    print(f"\n{post.name}")
    print(f"  {post.tagline}\n")
    print(f"  Votes:    {post.votes_count:,}")
    print(f"  Comments: {post.comments_count}")
    print(f"  Rating:   {post.reviews_rating or 'N/A'}")
    print(f"  Website:  {post.website}")

    # Get top comments (note: commenter usernames are redacted by API)
    comments = client.get_post_comments(
        post_slug=slug,
        first=5,
        order=CommentsOrder.VOTES_COUNT,
    )

    if comments.nodes:
        print("\n  Top Comments:\n")
        for c in comments.nodes:
            body = c.body[:100].replace("\n", " ")
            print(f"    ({c.votes_count} votes) {body}...")
            print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_competitors.py <product-slug>")
        print("Example: python analyze_competitors.py chatgpt")
        sys.exit(1)

    main(sys.argv[1])
