"""Parse Reddit JSON responses into Thread and Comment objects."""

from typing import Optional, Dict, Any, List
from .models import Thread, Comment


def _iter_comment_nodes(data: Dict[str, Any], comment_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Recursively extract all comment nodes from Reddit JSON structure."""
    comments = []
    
    if "children" not in data:
        return comments
    
    for child in data.get("children", []):
        if child.get("kind") != "t1":
            continue
        
        child_data = child.get("data", {})
        comment_id_value = child_data.get("id")
        
        # If filtering by comment ID, skip non-matching comments
        if comment_id and comment_id_value != comment_id:
            # Still check replies
            if "replies" in child_data and child_data["replies"]:
                comments.extend(_iter_comment_nodes(child_data["replies"], comment_id))
            continue
        
        comments.append(child_data)
        
        # Recursively get replies
        if "replies" in child_data and child_data["replies"]:
            comments.extend(_iter_comment_nodes(child_data["replies"], comment_id))
    
    return comments


def parse_reddit_thread_json(
    data: Dict[str, Any],
    comment_id: Optional[str] = None,
) -> Thread:
    """
    Parse Reddit JSON response into a Thread object.
    
    Args:
        data: JSON response from Reddit API
        comment_id: Optional comment ID to filter by
        
    Returns:
        Thread object with post and comments
    """
    # Extract post data (first element is the post)
    post_data = data[0]["data"]["children"][0]["data"]
    
    # Create Thread object
    thread = Thread(
        url=post_data.get("url", ""),
        subreddit=post_data.get("subreddit", ""),
        title=post_data.get("title", ""),
        post_id=post_data.get("id", ""),
        post_fullname=post_data.get("name", ""),
        permalink=post_data.get("permalink", ""),
        author=post_data.get("author", "[deleted]"),
        created_utc=post_data.get("created_utc"),
        score=post_data.get("score", 0),
        num_comments=post_data.get("num_comments", 0),
        raw_post=post_data,
    )
    
    # Extract comments (second element contains comments)
    if len(data) > 1:
        comments_data = data[1].get("data", {})
        comment_nodes = _iter_comment_nodes(comments_data, comment_id)
        
        for node in comment_nodes:
            comment = Comment(
                id=node.get("id", ""),
                body=node.get("body", ""),
                author=node.get("author", "[deleted]"),
                created_utc=node.get("created_utc"),
                score=node.get("score", 0),
                depth=node.get("depth", 0),
                parent_id=node.get("parent_id", ""),
                permalink=node.get("permalink", ""),
                raw=node,
            )
            thread.comments.append(comment)
    
    return thread
