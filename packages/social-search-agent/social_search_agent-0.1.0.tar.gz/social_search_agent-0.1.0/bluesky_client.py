import os
import sys
import requests
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

load_dotenv()

PUBLIC_API = "https://public.api.bsky.app/xrpc"
_client = None


def _get_auth_client():
    """Get authenticated client for search (requires auth)."""
    global _client
    if _client is None:
        handle = os.getenv("BLUESKY_HANDLE")
        password = os.getenv("BLUESKY_PASSWORD")
        if not handle or not password:
            raise ValueError("Set BLUESKY_HANDLE and BLUESKY_PASSWORD in .env")
        from atproto import Client
        _client = Client()
        _client.login(handle, password)
    return _client


def search_posts(query, limit=25, sort="latest"):
    """Search posts (requires auth)."""
    c = _get_auth_client()
    response = c.app.bsky.feed.search_posts({"q": query, "limit": limit, "sort": sort})
    return [{
        "uri": p.uri,
        "cid": p.cid,
        "author": p.author.handle,
        "text": p.record.text,
        "created_at": p.record.created_at,
        "like_count": p.like_count or 0,
        "reply_count": p.reply_count or 0,
    } for p in response.posts]


def get_thread(uri, depth=10):
    """Get post thread with replies (no auth)."""
    r = requests.get(f"{PUBLIC_API}/app.bsky.feed.getPostThread", params={"uri": uri, "depth": depth})
    r.raise_for_status()
    
    def parse(thread):
        post = thread.get("post", {})
        record = post.get("record", {})
        return {
            "uri": post.get("uri"),
            "author": post.get("author", {}).get("handle"),
            "text": record.get("text"),
            "created_at": record.get("createdAt"),
            "like_count": post.get("likeCount", 0),
            "replies": [parse(r) for r in thread.get("replies", []) if r.get("post")]
        }
    return parse(r.json().get("thread", {}))


def get_author_feed(handle, limit=25):
    """Get posts from a user (no auth)."""
    r = requests.get(f"{PUBLIC_API}/app.bsky.feed.getAuthorFeed", params={"actor": handle, "limit": limit})
    r.raise_for_status()
    return [{
        "uri": item.get("post", {}).get("uri"),
        "author": item.get("post", {}).get("author", {}).get("handle"),
        "text": item.get("post", {}).get("record", {}).get("text"),
        "created_at": item.get("post", {}).get("record", {}).get("createdAt"),
        "like_count": item.get("post", {}).get("likeCount", 0),
        "reply_count": item.get("post", {}).get("replyCount", 0),
    } for item in r.json().get("feed", [])]

