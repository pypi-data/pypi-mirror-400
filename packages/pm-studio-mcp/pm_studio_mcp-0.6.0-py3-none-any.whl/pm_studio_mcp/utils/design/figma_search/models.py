"""
Models for Figma search functionality.
"""
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass


@dataclass
class FigmaNode:
    """Represents a Figma node with minimal information."""
    type: str
    name: str
    link: str
    characters: Optional[str] = None
    children: Optional[List['FigmaNode']] = None


@dataclass
class FigmaSearchResult:
    """Result structure for Figma search operations."""
    resolved: Dict[str, Any]
    root: Dict[str, Any]
    children: List[Dict[str, Any]]


@dataclass
class FigmaError:
    """Error structure for Figma API errors."""
    message: str
    code: str
