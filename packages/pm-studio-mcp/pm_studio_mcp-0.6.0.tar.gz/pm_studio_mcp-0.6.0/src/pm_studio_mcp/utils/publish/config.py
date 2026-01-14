"""Configuration classes for GitHub Pages publishing."""

import os
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class PublishConfig:
    """Configuration for GitHub Pages publishing."""
    html_file_path: str
    repo_dir: str
    publish_branch: str = "reports"
    commit_message: str = "Publish HTML report to GitHub Pages"
    image_paths: Optional[List[str]] = None
    
    def __post_init__(self):
        """Validate and normalize paths after initialization."""
        self.html_file_path = os.path.abspath(self.html_file_path)
        self.repo_dir = os.path.abspath(self.repo_dir)
        
        if not os.path.isfile(self.html_file_path):
            raise FileNotFoundError(f"HTML file does not exist: {self.html_file_path}")
        
        if not os.path.isdir(self.repo_dir):
            raise FileNotFoundError(f"Repository directory does not exist: {self.repo_dir}")
