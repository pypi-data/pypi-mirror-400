"""Core scraping functionality."""

import re
from typing import Optional, Dict, Any
import requests
from .models import Thread, Comment
from .parser import parse_reddit_thread_json
from .fetch import fetch_url


def _extract_comment_id_from_url(url: str) -> Optional[str]:
    """Extract comment ID from URL if it's a comment-specific URL."""
    if '/comment/' in url:
        match = re.search(r'/comment/([a-zA-Z0-9]+)', url)
        if match:
            return match.group(1)
    return None


def scrape_thread(
    url: str,
    timeout: float = 60.0,
    proxies: Optional[Dict[str, str]] = None,
    delay: bool = True,
    return_raw: bool = False,
) -> Thread | Dict[str, Any]:
    """
    Scrape a single Reddit thread or comment.
    
    Args:
        url: Reddit thread or comment URL
        timeout: Request timeout in seconds
        proxies: Optional dict of proxies (http, https)
        delay: Whether to apply automatic delays for bot detection
        return_raw: Return raw JSON response instead of parsed Thread (default: False)
        
    Returns:
        Thread object with post and comments, or raw JSON dict if return_raw=True
        
    Raises:
        requests.RequestException: If the request fails
        ValueError: If the URL is invalid or parsing fails
    """
    # Get JSON data from Reddit
    json_data = fetch_url(url, timeout=timeout, proxies=proxies, delay=delay)
    
    # Return raw JSON if requested
    if return_raw:
        return json_data
    
    # Extract comment ID if this is a comment-specific URL
    comment_id = _extract_comment_id_from_url(url)
    
    # Parse the JSON response into Thread object
    thread = parse_reddit_thread_json(json_data, comment_id=comment_id)
    
    return thread
