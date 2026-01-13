#!/usr/bin/env python3
"""View your own Product Hunt profile and activity.

Usage:
    1. Create examples/.env with: PRODUCTHUNT_TOKEN=your_token
    2. Run: uv run python examples/my_profile.py
"""

import os

from dotenv import load_dotenv

from producthunt_sdk import BearerAuth, ProductHuntClient

load_dotenv()


def main():
    client = ProductHuntClient(auth=BearerAuth(os.getenv("PRODUCTHUNT_TOKEN", "")))

    # Get authenticated user
    viewer = client.get_viewer()
    if not viewer or not viewer.user:
        print("Could not get authenticated user. Check your token.")
        return

    user = viewer.user
    print(f"\n@{user.username}")
    print(f"  {user.name}")
    if user.headline:
        print(f"  {user.headline}")
    if user.twitter_username:
        print(f"  Twitter: @{user.twitter_username}")
    if user.website_url:
        print(f"  Website: {user.website_url}")

    # Get your products
    posts = client.get_user_posts(username=user.username, first=5)
    print(f"\nYour Products ({posts.total_count} total):")
    if posts.nodes:
        for post in posts.nodes:
            print(f"  - {post.name} ({post.votes_count} votes)")
            print(f"    {post.tagline}")
    else:
        print("  No products yet")

    # Get your votes
    votes = client.get_user_voted_posts(username=user.username, first=5)
    print(f"\nProducts You Voted ({votes.total_count} total):")
    if votes.nodes:
        for post in votes.nodes[:3]:
            print(f"  - {post.name}")
    else:
        print("  No votes yet")

    # Get your followers
    followers = client.get_user_followers(username=user.username, first=5)
    print(f"\nFollowers: {followers.total_count}")

    following = client.get_user_following(username=user.username, first=5)
    print(f"Following: {following.total_count}")


if __name__ == "__main__":
    main()
