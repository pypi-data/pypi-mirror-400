#!/usr/bin/env python3
"""Track your Product Hunt launch performance.

Usage:
    1. Create examples/.env with: PRODUCTHUNT_TOKEN=your_token
    2. Run: uv run python examples/track_launch.py your-product-slug
"""

import os
import sys

from dotenv import load_dotenv

from producthunt_sdk import BearerAuth, ProductHuntClient

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

    if post.makers:
        print("\n  Makers:")
        for maker in post.makers:
            print(f"    - {maker.name} (@{maker.username})")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python track_launch.py <product-slug>")
        print("Example: python track_launch.py chatgpt")
        sys.exit(1)

    main(sys.argv[1])
