#!/usr/bin/env python3
"""OAuth flow example for Product Hunt API.

Product Hunt requires HTTPS redirect URIs. Use ngrok to tunnel to localhost:

    1. Run: ngrok http 8000
    2. Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
    3. Register redirect URI in Product Hunt: https://abc123.ngrok.io/callback
    4. Set PRODUCTHUNT_REDIRECT_URI in .env to the same URL

Setup:
    Create examples/.env with:
       PRODUCTHUNT_CLIENT_ID=your_client_id
       PRODUCTHUNT_CLIENT_SECRET=your_client_secret
       PRODUCTHUNT_REDIRECT_URI=https://your-ngrok-url.ngrok.io/callback

Usage:
    # Start ngrok first: ngrok http 8000
    uv run python examples/oauth_flow.py
"""

import os

from dotenv import load_dotenv

from producthunt_sdk import OAuth2, ProductHuntClient

load_dotenv()


def main():
    client_id = os.getenv("PRODUCTHUNT_CLIENT_ID", "")
    client_secret = os.getenv("PRODUCTHUNT_CLIENT_SECRET", "")
    redirect_uri = os.getenv("PRODUCTHUNT_REDIRECT_URI", "")

    if not client_id or not client_secret:
        print("Set environment variables in examples/.env:")
        print("  PRODUCTHUNT_CLIENT_ID=your_client_id")
        print("  PRODUCTHUNT_CLIENT_SECRET=your_client_secret")
        print("  PRODUCTHUNT_REDIRECT_URI=https://your-ngrok-url.ngrok.io/callback")
        print("\nSetup:")
        print("  1. Run: ngrok http 8000")
        print("  2. Copy the HTTPS forwarding URL")
        print("  3. Register it at https://www.producthunt.com/v2/oauth/applications")
        return

    print("=" * 60)
    print("PRODUCT HUNT OAUTH FLOW")
    print("=" * 60)

    # Create OAuth2 auth - handles everything automatically!
    # On first API call, it will:
    # 1. Open browser for authorization
    # 2. Run local callback server
    # 3. Exchange code for token
    # 4. Cache token for future use
    auth = OAuth2(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri if redirect_uri else None,
        scope="public private",
    )

    client = ProductHuntClient(auth=auth)

    print("\nMake sure ngrok is running: ngrok http 8000")
    print("Browser will open for authorization...")
    print()

    # This triggers the OAuth flow automatically
    viewer = client.get_viewer()

    if viewer and viewer.user:
        print("\n" + "=" * 60)
        print("SUCCESS!")
        print("=" * 60)
        print(f"\nAuthenticated as: @{viewer.user.username}")
        print(f"Name: {viewer.user.name}")

        posts = client.get_user_posts(username=viewer.user.username, first=5)
        print(f"Your posts: {posts.total_count}")

        votes = client.get_user_voted_posts(username=viewer.user.username, first=5)
        print(f"Your votes: {votes.total_count}")

        followers = client.get_user_followers(username=viewer.user.username, first=5)
        print(f"Your followers: {followers.total_count}")

        print("\nToken is cached - subsequent runs won't require re-authorization.")
        print("To force re-auth, call: auth.clear_token()")
    else:
        print("Could not get authenticated user")


if __name__ == "__main__":
    main()
