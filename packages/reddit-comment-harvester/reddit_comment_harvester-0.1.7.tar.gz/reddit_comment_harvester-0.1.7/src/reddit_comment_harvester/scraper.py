"""Main RedditScraper class."""

from __future__ import annotations

from typing import Dict, List, Optional
import csv

from .scrape import scrape_thread
from .models import Thread


class RedditScraper:
    """
    Main class for scraping Reddit threads and comments.
    
    Example:
        scraper = RedditScraper()
        thread = scraper.scrape("https://reddit.com/r/python/comments/abc123/")
        print(f"{thread.title}: {len(thread.comments)} comments")
    """

    def __init__(
        self,
        timeout: float = 60.0,
        delay: bool = True,
        proxies: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize the Reddit scraper.

        Args:
            timeout: Request timeout in seconds (default: 60.0)
            delay: Apply random delays between requests (default: True)
            proxies: Optional proxy configuration (default: None)
        """
        self.timeout = timeout
        self.delay = delay
        self.proxies = proxies

    def scrape(self, url: str, return_raw: bool = False) -> Thread | dict:
        """
        Scrape a single Reddit thread.

        Args:
            url: Reddit thread URL
            return_raw: Return raw JSON response instead of parsed Thread object (default: False)

        Returns:
            Thread object with post and comments, or raw JSON dict if return_raw=True
        """
        return scrape_thread(url, timeout=self.timeout, proxies=self.proxies, delay=self.delay, return_raw=return_raw)

    def scrape_batch(self, urls: List[str], skip_errors: bool = True) -> List[Thread]:
        """
        Scrape multiple URLs and return results.

        Args:
            urls: List of Reddit thread URLs
            skip_errors: Skip URLs that fail (default: True)

        Returns:
            List of Thread objects
        """
        threads = []
        for url in urls:
            try:
                thread = self.scrape(url)
                threads.append(thread)
            except Exception as e:
                if not skip_errors:
                    raise
        return threads

    def scrape_csv(
        self,
        input_file: str,
        output_file: Optional[str] = None,
        url_column: str = "URL",
        skip_errors: bool = True,
    ) -> List[dict]:
        """
        Scrape URLs from a CSV file and optionally save results.

        Args:
            input_file: Path to input CSV file
            output_file: Path to output CSV file (optional)
            url_column: Name of column containing URLs (default: "URL")
            skip_errors: Skip URLs that fail (default: True)

        Returns:
            List of result dictionaries
        """
        results = []
        urls = []
        
        # Read input CSV
        with open(input_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                urls.append(row[url_column])
        
        # Scrape URLs
        threads = self.scrape_batch(urls, skip_errors=skip_errors)
        
        # Convert to results
        for thread in threads:
            result = {
                "url": thread.url,
                "title": thread.title,
                "subreddit": thread.subreddit,
                "author": thread.author,
                "score": thread.score,
                "num_comments": len(thread.comments),
            }
            results.append(result)
        
        # Write output CSV if requested
        if output_file and results:
            with open(output_file, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
        
        return results

    def set_timeout(self, timeout: float) -> None:
        """Set request timeout in seconds."""
        self.timeout = timeout

    def set_delay(self, delay: bool) -> None:
        """Enable or disable request delays."""
        self.delay = delay

    def set_proxy(self, proxies: Optional[Dict[str, str]]) -> None:
        """Set proxy configuration."""
        self.proxies = proxies
