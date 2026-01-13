#!/usr/bin/env python3
"""Test script for ClientCredentials authentication."""

import os

from dotenv import load_dotenv

from producthunt_sdk import ClientCredentials, ProductHuntClient

load_dotenv()


def main():
    client_id = os.environ.get("PRODUCTHUNT_CLIENT_ID")
    client_secret = os.environ.get("PRODUCTHUNT_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("Error: Set PRODUCTHUNT_CLIENT_ID and PRODUCTHUNT_CLIENT_SECRET in .env")
        return

    print("Creating client with ClientCredentials auth...")
    auth = ClientCredentials(client_id=client_id, client_secret=client_secret)
    client = ProductHuntClient(auth=auth)

    print("\n--- Fetching featured posts ---")
    posts = client.get_posts(featured=True, first=5)
    print(f"Found {len(posts.nodes)} posts:\n")

    for post in posts.nodes:
        print(f"  {post.name}")
        print(f"    {post.tagline}")
        print(f"    Votes: {post.votes_count} | Comments: {post.comments_count}")
        print(f"    is_voted: {post.is_voted} (always False with client credentials)")
        print()

    print("--- Fetching topics ---")
    topics = client.get_topics(first=5)
    for topic in topics.nodes:
        print(f"  {topic.name}: {topic.followers_count} followers")

    print("\n--- Testing viewer (should be None) ---")
    viewer = client.get_viewer()
    print(f"  viewer: {viewer}")

    print("\nClientCredentials auth working correctly!")
    client.close()


if __name__ == "__main__":
    main()
