"""HTTP request layer with bot detection evasion."""

import time
import random
from typing import Optional, Dict, Any
import requests


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
]

DEFAULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "DNT": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
}


class SmartSession:
    """Session with automatic delays and User-Agent rotation for bot detection evasion."""
    
    def __init__(self):
        self.session = requests.Session()
        self._last_request_time = 0
    
    def _apply_delay(self) -> None:
        """Apply a random 2-6 second delay between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < 2:
            delay = random.uniform(2, 6)
            time.sleep(delay)
    
    def _rotate_user_agent(self) -> str:
        """Select a random User-Agent from the pool."""
        return random.choice(USER_AGENTS)
    
    def get(
        self,
        url: str,
        timeout: float = 60.0,
        proxies: Optional[Dict[str, str]] = None,
        delay: bool = True,
    ) -> requests.Response:
        """Make a GET request with bot evasion headers."""
        if delay:
            self._apply_delay()
        
        headers = DEFAULT_HEADERS.copy()
        headers["User-Agent"] = self._rotate_user_agent()
        
        response = self.session.get(
            url,
            headers=headers,
            timeout=timeout,
            proxies=proxies,
        )
        response.raise_for_status()
        
        self._last_request_time = time.time()
        return response


# Global session instance
_session = SmartSession()


def fetch_url(
    url: str,
    timeout: float = 60.0,
    proxies: Optional[Dict[str, str]] = None,
    delay: bool = True,
) -> Dict[str, Any]:
    """
    Fetch JSON data from a Reddit URL.
    
    Args:
        url: Reddit thread or comment URL
        timeout: Request timeout in seconds
        proxies: Optional proxy configuration
        delay: Apply automatic delays for bot detection evasion
        
    Returns:
        Parsed JSON response from Reddit
        
    Raises:
        requests.RequestException: If the request fails
    """
    # Convert Reddit URL to JSON endpoint
    if url.endswith("/"):
        json_url = url + ".json"
    else:
        json_url = url + ".json"
    
    # Make request
    response = _session.get(json_url, timeout=timeout, proxies=proxies, delay=delay)
    
    # Parse and return JSON
    return response.json()
