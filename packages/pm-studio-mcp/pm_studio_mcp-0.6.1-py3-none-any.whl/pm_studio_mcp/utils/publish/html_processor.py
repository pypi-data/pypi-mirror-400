"""HTML file processing utilities for GitHub Pages publishing."""

import os
import re
from typing import Dict, Tuple

from .exceptions import FileProcessingError


class HtmlProcessor:
    """Handles HTML file processing and image path fixing."""
    
    @staticmethod
    def parse_image_references(html_file_path: str) -> Dict[str, str]:
        """Parse HTML file to extract image references and their relative paths.
        
        Args:
            html_file_path: Path to the HTML file to parse
            
        Returns:
            Dictionary mapping image filenames to their src paths in HTML
            
        Raises:
            FileProcessingError: If the HTML file cannot be read or parsed
        """
        if not os.path.isfile(html_file_path):
            raise FileProcessingError(f"HTML file does not exist: {html_file_path}")
        
        image_references = {}
        
        try:
            with open(html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            img_pattern = r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>'
            matches = re.findall(img_pattern, html_content, re.IGNORECASE)
            
            for src_path in matches:
                # Skip external URLs and absolute paths
                if (src_path.startswith(('http://', 'https://', '//', 'data:', 'blob:')) or 
                    src_path.startswith('/')):
                    continue
                
                filename = os.path.basename(src_path)
                if filename:
                    image_references[filename] = src_path
                    
        except Exception as e:
            raise FileProcessingError(f"Could not parse HTML file {html_file_path}: {e}")
        
        return image_references
    
    @staticmethod
    def fix_image_paths(html_file_path: str) -> Tuple[str, Dict[str, str]]:
        """Fix invalid image paths in HTML file.
        
        This method replaces paths that start with '..', '/', or '\' with 
        standardized 'assets/images/' paths.
        
        Args:
            html_file_path: Path to the HTML file to fix
            
        Returns:
            Tuple of (html_file_path, mapping of filename to new path)
            
        Raises:
            FileProcessingError: If the HTML file cannot be read or written
        """
        if not os.path.isfile(html_file_path):
            raise FileProcessingError(f"HTML file does not exist: {html_file_path}")
        
        try:
            with open(html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            img_pattern = r'<img([^>]+)src=["\\\']([^"\\\']+)["\\\']([^>]*)>'
            matches = list(re.finditer(img_pattern, html_content, re.IGNORECASE))
            filename_to_newpath = {}
            new_html = html_content
            
            for m in matches:
                before, src_path, after = m.group(1), m.group(2), m.group(3)
                filename = os.path.basename(src_path)
                
                if src_path.startswith('..') or src_path.startswith('/') or src_path.startswith('\\'):
                    new_src = f"assets/images/{filename}"
                    filename_to_newpath[filename] = new_src
                    new_img = f'<img{before}src="{new_src}"{after}>'
                    new_html = new_html.replace(m.group(0), new_img)
            
            if filename_to_newpath:
                with open(html_file_path, 'w', encoding='utf-8') as f:
                    f.write(new_html)
            
            return html_file_path, filename_to_newpath
            
        except Exception as e:
            raise FileProcessingError(f"Failed to fix image paths in {html_file_path}: {e}")
