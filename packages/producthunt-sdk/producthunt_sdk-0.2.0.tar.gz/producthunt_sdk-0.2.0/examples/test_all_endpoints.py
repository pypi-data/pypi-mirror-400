#!/usr/bin/env python3
"""Test all SDK endpoints manually.

This script calls every method in the SDK and prints results/errors.
Use it to validate the SDK works correctly with the real API.

NOTE: Product Hunt's API has privacy restrictions:
- Public data (posts, topics, collections): Full access
- Your own user data: Full access
- Other users' data: Redacted (returns 0/empty)

Usage:
    1. Create examples/.env with OAuth credentials:
       PRODUCTHUNT_CLIENT_ID=your_client_id
       PRODUCTHUNT_CLIENT_SECRET=your_client_secret
       PRODUCTHUNT_REDIRECT_URI=https://your-ngrok-url.ngrok.io/callback
    2. Start ngrok: ngrok http 8000
    3. Run: uv run python examples/test_all_endpoints.py
"""

import os

from dotenv import load_dotenv

from producthunt_sdk import (
    AuthenticationError,
    CollectionsOrder,
    CommentsOrder,
    GraphQLError,
    OAuth2,
    PostsOrder,
    ProductHuntClient,
    ProductHuntError,
    RateLimitError,
    TopicsOrder,
)

load_dotenv()


def test(name: str, func):
    """Run a test and print result or error."""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print("=" * 60)
    try:
        result = func()
        if result is None:
            print("  Result: None (not found)")
        elif hasattr(result, "nodes"):
            print(f"  Result: {len(result.nodes)} items (total: {result.total_count})")
            for item in result.nodes[:3]:
                if hasattr(item, "name"):
                    print(f"    - {item.name}")
                elif hasattr(item, "username"):
                    print(f"    - @{item.username}")
                elif hasattr(item, "body"):
                    print(f"    - {item.body[:50]}...")
                elif hasattr(item, "user"):
                    print(f"    - Vote by @{item.user.username if item.user else 'unknown'}")
        elif hasattr(result, "name"):
            print(f"  Result: {result.name}")
        elif hasattr(result, "username"):
            print(f"  Result: @{result.username}")
        elif hasattr(result, "user"):
            print(f"  Result: Viewer @{result.user.username}")
        else:
            print(f"  Result: {result}")
        return True
    except AuthenticationError as e:
        print(f"  AUTH ERROR: {e}")
        return False
    except RateLimitError as e:
        print(f"  RATE LIMIT: {e}")
        return False
    except GraphQLError as e:
        print(f"  GRAPHQL ERROR: {e}")
        return False
    except ProductHuntError as e:
        print(f"  ERROR: {e}")
        return False
    except Exception as e:
        print(f"  UNEXPECTED ERROR: {type(e).__name__}: {e}")
        return False


def main():
    client_id = os.getenv("PRODUCTHUNT_CLIENT_ID", "")
    client_secret = os.getenv("PRODUCTHUNT_CLIENT_SECRET", "")
    redirect_uri = os.getenv("PRODUCTHUNT_REDIRECT_URI", "")

    if not client_id or not client_secret or not redirect_uri:
        print("Set OAuth credentials in examples/.env:")
        print("  PRODUCTHUNT_CLIENT_ID=your_client_id")
        print("  PRODUCTHUNT_CLIENT_SECRET=your_client_secret")
        print("  PRODUCTHUNT_REDIRECT_URI=https://your-ngrok-url.ngrok.io/callback")
        print("\nSetup:")
        print("  1. Run: ngrok http 8000")
        print("  2. Copy the HTTPS forwarding URL")
        print("  3. Register it at https://www.producthunt.com/v2/oauth/applications")
        return

    auth = OAuth2(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope="public private",
    )

    client = ProductHuntClient(auth=auth)
    results = []

    print("\n" + "#" * 60)
    print("# PRODUCT HUNT SDK - ENDPOINT TESTS")
    print("#" * 60)

    # =====================================================================
    # POSTS
    # =====================================================================
    results.append(test(
        "get_post(slug)",
        lambda: client.get_post(slug="chatgpt")
    ))

    results.append(test(
        "get_posts(featured)",
        lambda: client.get_posts(featured=True, first=5)
    ))

    results.append(test(
        "get_posts(topic, order)",
        lambda: client.get_posts(topic="artificial-intelligence", order=PostsOrder.VOTES, first=5)
    ))

    results.append(test(
        "get_post_comments(post_slug, order)",
        lambda: client.get_post_comments(post_slug="chatgpt", order=CommentsOrder.VOTES_COUNT, first=5)
    ))

    results.append(test(
        "get_post_votes(post_slug)",
        lambda: client.get_post_votes(post_slug="chatgpt", first=5)
    ))

    # =====================================================================
    # USERS
    # Note: API only returns full data for the authenticated user.
    # Other users' data is redacted for privacy.
    # =====================================================================

    # Get the authenticated user to test with their data
    viewer = client.get_viewer()
    if viewer and viewer.user:
        test_username = viewer.user.username
    else:
        print("  Could not get authenticated user")
        test_username = None

    print(f"\n  (Testing user endpoints with @{test_username})")

    results.append(test(
        f"get_user(username) {test_username}",
        lambda: client.get_user(username=test_username)
    ))

    results.append(test(
        f"get_user_posts(username) {test_username}",
        lambda: client.get_user_posts(username=test_username, first=5)
    ))

    results.append(test(
        f"get_user_voted_posts(username) {test_username}",
        lambda: client.get_user_voted_posts(username=test_username, first=5)
    ))

    results.append(test(
        f"get_user_followers(username) {test_username}",
        lambda: client.get_user_followers(username=test_username, first=5)
    ))

    results.append(test(
        f"get_user_following(username) {test_username}",
        lambda: client.get_user_following(username=test_username, first=5)
    ))

    # =====================================================================
    # TOPICS
    # =====================================================================
    results.append(test(
        "get_topic(slug)",
        lambda: client.get_topic(slug="artificial-intelligence")
    ))

    results.append(test(
        "get_topics(order)",
        lambda: client.get_topics(order=TopicsOrder.FOLLOWERS_COUNT, first=5)
    ))

    # =====================================================================
    # COLLECTIONS
    # =====================================================================
    results.append(test(
        "get_collections(order)",
        lambda: client.get_collections(order=CollectionsOrder.FOLLOWERS_COUNT, first=5)
    ))

    # Get a collection ID for further tests
    collections = client.get_collections(first=1)
    if collections.nodes:
        collection_id = collections.nodes[0].id

        results.append(test(
            "get_collection(id)",
            lambda: client.get_collection(id=collection_id)
        ))

        results.append(test(
            "get_collection_posts(collection_id)",
            lambda: client.get_collection_posts(collection_id=collection_id, first=5)
        ))

    # =====================================================================
    # COMMENTS
    # =====================================================================
    # Get a comment ID for the test
    comments = client.get_post_comments(post_slug="chatgpt", first=1)
    if comments.nodes:
        comment_id = comments.nodes[0].id

        results.append(test(
            "get_comment(id)",
            lambda: client.get_comment(id=comment_id)
        ))

    # =====================================================================
    # VIEWER
    # =====================================================================
    results.append(test(
        "get_viewer()",
        lambda: client.get_viewer()
    ))

    # # =====================================================================
    # # CUSTOM GRAPHQL
    # # =====================================================================
    results.append(test(
        "graphql(custom query)",
        lambda: client.graphql("""
            query {
                posts(first: 3, featured: true) {
                    edges {
                        node {
                            name
                            votesCount
                        }
                    }
                }
            }
        """)
    ))

    # =====================================================================
    # MUTATIONS (commented out - these modify data)
    # =====================================================================
    # Uncomment to test mutations:
    
    # results.append(test(
    #     "follow_user(user_id)",
    #     lambda: client.follow_user(user_id="some_user_id")
    # ))
    
    # results.append(test(
    #     "unfollow_user(user_id)",
    #     lambda: client.unfollow_user(user_id="some_user_id")
    # ))

    # =====================================================================
    # RATE LIMIT INFO
    # =====================================================================
    print(f"\n{'='*60}")
    print("RATE LIMIT STATUS")
    print("=" * 60)
    info = client.rate_limit_info
    print(f"  Remaining: {info.remaining} / {info.limit}")
    print(f"  Resets in: {info.seconds_until_reset:.0f} seconds")

    # =====================================================================
    # SUMMARY
    # =====================================================================
    passed = sum(results)
    total = len(results)
    print(f"\n{'='*60}")
    print(f"SUMMARY: {passed}/{total} tests passed")
    print("=" * 60)

    if passed < total:
        print("\nFailed tests may indicate:")
        print("  - Invalid API token")
        print("  - Rate limiting")
        print("  - API changes")
        print("  - Network issues")


if __name__ == "__main__":
    main()
