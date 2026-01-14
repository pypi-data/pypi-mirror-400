"""
Motion (appmotion.design) Configuration
"""

from dataclasses import dataclass
from typing import Literal


@dataclass
class MotionConfig:
    headless: bool = True
    timeout: int = 30000  # ms
    user_agent: str = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    max_items: int = 10
    max_scrolls: int = 6
    scroll_delay_ms: int = 600
    wait_until: Literal["load", "domcontentloaded", "networkidle"] = "networkidle"
    # Debug options
    debug: bool = False
    debug_dir: str = "working_dir/motion_debug"
    # Deep extraction options (video-only mode by default)
    deep_extract_media: bool = True
    detail_timeout_ms: int = 15000
    max_detail_visits: int = 12

    def to_dict(self) -> dict:
        return {
            "headless": self.headless,
            "timeout": self.timeout,
            "max_items": self.max_items,
            "max_scrolls": self.max_scrolls,
            "scroll_delay_ms": self.scroll_delay_ms,
            "wait_until": self.wait_until,
            "debug": self.debug,
            "debug_dir": self.debug_dir,
            "deep_extract_media": self.deep_extract_media,
            "detail_timeout_ms": self.detail_timeout_ms,
            "max_detail_visits": self.max_detail_visits,
        }
