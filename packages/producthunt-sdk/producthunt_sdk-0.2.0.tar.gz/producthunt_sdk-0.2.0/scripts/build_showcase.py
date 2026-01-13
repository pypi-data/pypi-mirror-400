#!/usr/bin/env python3
"""Build a static HTML showcase page with Product Hunt data."""

import os
from datetime import datetime, timezone
from pathlib import Path

from producthunt_sdk import BearerAuth, ProductHuntClient


def get_product_hunt_data(client: ProductHuntClient) -> dict:
    """Fetch data from Product Hunt API."""
    # Get today's featured products
    posts = client.get_posts(featured=True, first=10)

    # Get top topics
    topics = client.get_topics(first=6)

    # Calculate stats
    total_votes = sum(p.votes_count for p in posts.nodes)
    total_comments = sum(p.comments_count for p in posts.nodes)

    return {
        "posts": posts.nodes,
        "topics": topics.nodes,
        "total_votes": total_votes,
        "total_comments": total_comments,
        "post_count": len(posts.nodes),
    }


def generate_html(data: dict) -> str:
    """Generate HTML page with bento grid layout."""
    posts = data["posts"]
    topics = data["topics"]

    # Generate post cards
    post_cards = ""
    for i, post in enumerate(posts):
        size_class = "large" if i == 0 else "small"
        thumbnail = post.thumbnail.url if post.thumbnail else ""
        thumbnail_html = f'<img src="{thumbnail}" alt="{post.name}" class="thumbnail">' if thumbnail else '<div class="thumbnail-placeholder"></div>'

        post_cards += f'''
        <div class="bento-item {size_class}">
            <a href="{post.url}" target="_blank" class="post-link">
                {thumbnail_html}
                <div class="post-content">
                    <h3>{post.name}</h3>
                    <p class="tagline">{post.tagline}</p>
                    <div class="post-meta">
                        <span class="votes"><svg viewBox="0 0 24 24" width="16" height="16"><path fill="currentColor" d="M12 4l-8 8h5v8h6v-8h5z"/></svg> {post.votes_count}</span>
                        <span class="comments"><svg viewBox="0 0 24 24" width="16" height="16"><path fill="currentColor" d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/></svg> {post.comments_count}</span>
                    </div>
                </div>
            </a>
        </div>'''

    # Generate topic tags
    topic_tags = "".join(
        f'<span class="topic-chip">{t.name}</span>'
        for t in topics
    )

    # Top product highlight
    top_post = posts[0] if posts else None
    top_product_html = ""
    if top_post:
        top_thumbnail = top_post.thumbnail.url if top_post.thumbnail else ""
        top_product_html = f'''
        <div class="top-product">
            <div class="rank-badge">#1</div>
            <img src="{top_thumbnail}" alt="{top_post.name}" class="top-thumbnail">
            <div class="top-info">
                <h2>{top_post.name}</h2>
                <p>{top_post.tagline}</p>
                <div class="top-stats">
                    <span>{top_post.votes_count} upvotes</span>
                    <span>{top_post.comments_count} comments</span>
                </div>
            </div>
        </div>'''

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Product Hunt Today - Live Showcase</title>
    <meta name="description" content="Live showcase of today's top products on Product Hunt, powered by producthunt-sdk">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-primary: #0a0a0a;
            --bg-secondary: #141414;
            --bg-tertiary: #1a1a1a;
            --text-primary: #ffffff;
            --text-secondary: #a0a0a0;
            --accent: #ff6154;
            --accent-hover: #ff7a70;
            --border: #2a2a2a;
            --gradient-1: linear-gradient(135deg, #ff6154 0%, #ff9a8b 100%);
            --gradient-2: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            line-height: 1.6;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }}

        header {{
            text-align: center;
            margin-bottom: 3rem;
        }}

        header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            background: var(--gradient-1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
        }}

        header p {{
            color: var(--text-secondary);
            font-size: 1.1rem;
        }}

        .stats-bar {{
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin: 2rem 0;
            flex-wrap: wrap;
        }}

        .stat-item {{
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem 2rem;
            text-align: center;
            min-width: 150px;
        }}

        .stat-value {{
            font-size: 2rem;
            font-weight: 700;
            color: var(--accent);
        }}

        .stat-label {{
            color: var(--text-secondary);
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .bento-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1.5rem;
            margin-bottom: 3rem;
        }}

        .bento-item {{
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 16px;
            overflow: hidden;
            transition: transform 0.2s, border-color 0.2s;
        }}

        .bento-item:hover {{
            transform: translateY(-4px);
            border-color: var(--accent);
        }}

        .bento-item.large {{
            grid-column: span 2;
            grid-row: span 2;
        }}

        .post-link {{
            display: block;
            text-decoration: none;
            color: inherit;
            height: 100%;
        }}

        .thumbnail {{
            width: 100%;
            height: 200px;
            object-fit: cover;
        }}

        .large .thumbnail {{
            height: 300px;
        }}

        .thumbnail-placeholder {{
            width: 100%;
            height: 200px;
            background: var(--gradient-2);
        }}

        .large .thumbnail-placeholder {{
            height: 300px;
        }}

        .post-content {{
            padding: 1.25rem;
        }}

        .large .post-content {{
            padding: 1.5rem;
        }}

        .post-content h3 {{
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }}

        .large .post-content h3 {{
            font-size: 1.5rem;
        }}

        .tagline {{
            color: var(--text-secondary);
            font-size: 0.875rem;
            margin-bottom: 1rem;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}

        .post-meta {{
            display: flex;
            gap: 1rem;
            margin-bottom: 0.75rem;
        }}

        .post-meta span {{
            display: flex;
            align-items: center;
            gap: 0.25rem;
            color: var(--text-secondary);
            font-size: 0.875rem;
        }}

        .votes {{
            color: var(--accent) !important;
        }}

        .topics-section {{
            margin-bottom: 3rem;
        }}

        .topics-section h2 {{
            font-size: 1.25rem;
            margin-bottom: 1rem;
            color: var(--text-secondary);
        }}

        .topic-chips {{
            display: flex;
            gap: 0.75rem;
            flex-wrap: wrap;
        }}

        .topic-chip {{
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            color: var(--text-primary);
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.875rem;
            transition: border-color 0.2s;
        }}

        .topic-chip:hover {{
            border-color: var(--accent);
        }}

        footer {{
            text-align: center;
            padding: 2rem;
            border-top: 1px solid var(--border);
            color: var(--text-secondary);
        }}

        footer a {{
            color: var(--accent);
            text-decoration: none;
        }}

        footer a:hover {{
            text-decoration: underline;
        }}

        .update-time {{
            font-size: 0.875rem;
            margin-top: 0.5rem;
        }}

        @media (max-width: 1024px) {{
            .bento-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
            .bento-item.large {{
                grid-column: span 2;
                grid-row: span 1;
            }}
        }}

        @media (max-width: 640px) {{
            .container {{
                padding: 1rem;
            }}
            .bento-grid {{
                grid-template-columns: 1fr;
            }}
            .bento-item.large {{
                grid-column: span 1;
            }}
            .stats-bar {{
                gap: 1rem;
            }}
            .stat-item {{
                min-width: 100px;
                padding: 1rem;
            }}
            header h1 {{
                font-size: 1.75rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Product Hunt Today</h1>
            <p>Live showcase powered by <a href="https://github.com/Domoryonok/producthunt-sdk" style="color: var(--accent);">producthunt-sdk</a></p>
        </header>

        <div class="stats-bar">
            <div class="stat-item">
                <div class="stat-value">{data["post_count"]}</div>
                <div class="stat-label">Products</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{data["total_votes"]:,}</div>
                <div class="stat-label">Total Votes</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{data["total_comments"]:,}</div>
                <div class="stat-label">Comments</div>
            </div>
        </div>

        <div class="bento-grid">
            {post_cards}
        </div>

        <div class="topics-section">
            <h2>Trending Topics</h2>
            <div class="topic-chips">
                {topic_tags}
            </div>
        </div>

        <footer>
            <p>Built with <a href="https://github.com/Domoryonok/producthunt-sdk">producthunt-sdk</a> - A Python SDK for the Product Hunt API</p>
            <p class="update-time">Last updated: {now}</p>
        </footer>
    </div>
</body>
</html>'''


def main():
    """Main function to build the showcase page."""
    # Get token from environment
    token = os.environ.get("DEVELOPER_TOKEN")
    if not token:
        raise RuntimeError("DEVELOPER_TOKEN environment variable is required")

    # Create client
    client = ProductHuntClient(auth=BearerAuth(token))

    try:
        # Fetch data
        print("Fetching Product Hunt data...")
        data = get_product_hunt_data(client)
        print(f"Found {data['post_count']} products with {data['total_votes']} total votes")

        # Generate HTML
        print("Generating HTML...")
        html = generate_html(data)

        # Write to file
        output_dir = Path("public")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / "index.html"
        output_path.write_text(html)
        print(f"Showcase page built: {output_path}")

    finally:
        client.close()


if __name__ == "__main__":
    main()
