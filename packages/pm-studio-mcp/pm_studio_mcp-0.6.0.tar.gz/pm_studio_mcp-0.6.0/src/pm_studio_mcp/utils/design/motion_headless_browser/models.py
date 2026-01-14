"""
Data models for appmotion.design search results.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class MotionItem:
    title: Optional[str]
    thumb_url: Optional[str]
    media_url: Optional[str]
    link_url: Optional[str]
    author: Optional[str] = None
    tags: Optional[List[str]] = None

    def to_dict(self) -> dict:
        # Video-only response: do not include thumb_url to avoid clients rendering thumbnails
        return {
            "title": self.title,
            "media_url": self.media_url,
            "link_url": self.link_url,
            "author": self.author,
            "tags": self.tags or [],
        }


@dataclass
class MotionSearchResult:
    query: str
    items: List[MotionItem]
    total_found: int
    status: str = "success"
    message: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "query": self.query,
            "total_found": self.total_found,
            "items_returned": len(self.items),
            "items": [i.to_dict() for i in self.items],
            "message": self.message,
        }
