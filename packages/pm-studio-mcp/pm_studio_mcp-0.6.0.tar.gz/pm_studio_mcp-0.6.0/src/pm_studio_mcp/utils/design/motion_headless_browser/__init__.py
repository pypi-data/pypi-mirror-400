"""
AppMotion (appmotion.design) Headless Browser Module

Search and extract motion design previews from appmotion.design using Playwright.
No authentication required.
"""

from .searcher import MotionSearcher, search_motion

__all__ = ["MotionSearcher", "search_motion"]
