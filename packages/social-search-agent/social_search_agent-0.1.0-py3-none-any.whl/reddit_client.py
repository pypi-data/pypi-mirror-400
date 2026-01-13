import os
from dotenv import load_dotenv
import praw

load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    username=os.getenv("REDDIT_USERNAME"),
    password=os.getenv("REDDIT_PASSWORD"),
    user_agent="SocialSearch/1.0"
)


def search_subreddit(subreddit_name, query, limit=10, sort="relevance", time_filter="all"):
    """Search posts in a subreddit."""
    sub = reddit.subreddit(subreddit_name)
    return [{
        "id": post.id,
        "title": post.title,
        "author": str(post.author),
        "score": post.score,
        "url": post.url,
        "selftext": post.selftext,
        "num_comments": post.num_comments,
        "created_utc": post.created_utc,
        "permalink": f"https://reddit.com{post.permalink}"
    } for post in sub.search(query, sort=sort, time_filter=time_filter, limit=limit)]


def get_post(post_id):
    """Get full post by ID."""
    post = reddit.submission(id=post_id)
    return {
        "id": post.id,
        "title": post.title,
        "author": str(post.author),
        "score": post.score,
        "url": post.url,
        "selftext": post.selftext,
        "num_comments": post.num_comments,
        "created_utc": post.created_utc,
        "permalink": f"https://reddit.com{post.permalink}"
    }


def get_comments(post_id, limit=0):
    """Get comments for a post. limit=0 removes 'more comments' stubs."""
    post = reddit.submission(id=post_id)
    post.comments.replace_more(limit=limit)
    return [{
        "id": c.id,
        "author": str(c.author),
        "body": c.body,
        "score": c.score,
        "created_utc": c.created_utc,
        "parent_id": c.parent_id,
        "is_top_level": c.parent_id.startswith("t3_")
    } for c in post.comments.list()]

