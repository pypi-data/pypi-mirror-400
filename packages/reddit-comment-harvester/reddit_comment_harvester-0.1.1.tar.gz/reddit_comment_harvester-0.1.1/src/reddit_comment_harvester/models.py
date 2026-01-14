"""Data models for Reddit threads and comments."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Comment:
    """Represents a single Reddit comment."""
    
    id: str
    body: str
    author: Optional[str] = None
    created_utc: Optional[float] = None
    score: Optional[int] = None
    depth: int = 0
    parent_id: Optional[str] = None
    permalink: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Thread:
    """Represents a Reddit thread (post + comments)."""
    
    url: str
    subreddit: Optional[str] = None
    title: Optional[str] = None
    post_id: Optional[str] = None
    post_fullname: Optional[str] = None
    permalink: Optional[str] = None
    author: Optional[str] = None
    created_utc: Optional[float] = None
    score: Optional[int] = None
    num_comments: Optional[int] = None
    comments: List[Comment] = field(default_factory=list)
    raw_post: Dict[str, Any] = field(default_factory=dict)
