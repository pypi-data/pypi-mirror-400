"""Image file management for GitHub Pages publishing."""

import os
import shutil
from typing import Dict, List, Tuple

from .exceptions import FileProcessingError


class ImageManager:
    """Handles image file operations."""
    
    def __init__(self, repo_dir: str):
        """Initialize with repository directory."""
        self.repo_dir = repo_dir
        if not os.path.isdir(repo_dir):
            raise FileNotFoundError(f"Repository directory does not exist: {repo_dir}")
    
    def match_images_to_html_paths(self, image_paths: List[str], html_references: Dict[str, str]) -> List[Tuple[str, str]]:
        """Match provided image files to their corresponding paths in HTML.
        
        Args:
            image_paths: List of absolute paths to image files
            html_references: Dictionary mapping filenames to their HTML src paths
            
        Returns:
            List of tuples (image_path, target_relative_path)
        """
        matched_images = []
        unmatched_images = []
        
        for image_path in image_paths:
            if not os.path.isfile(image_path):
                print(f"Warning: Image file {image_path} does not exist, skipping...")
                continue
                
            filename = os.path.basename(image_path)
            
            if filename in html_references:
                target_path = html_references[filename]
                matched_images.append((image_path, target_path))
            else:
                target_path = f"assets/images/{filename}"
                matched_images.append((image_path, target_path))
                unmatched_images.append(filename)
        
        if unmatched_images:
            print(f"Warning: {len(unmatched_images)} image(s) not found in HTML references:")
            for filename in unmatched_images:
                print(f"  - {filename} -> using fallback path: assets/images/{filename}")
        
        return matched_images
    
    def copy_images(self, matched_images: List[Tuple[str, str]], fixed_img_map: Dict[str, str]) -> Tuple[List[str], List[str]]:
        """Copy images to target locations and return copied files and failed images.
        
        Args:
            matched_images: List of (source_path, target_relative_path) tuples
            fixed_img_map: Dictionary mapping filenames to fixed paths
            
        Returns:
            Tuple of (copied_files, failed_images) where:
            - copied_files: List of relative paths of successfully copied files
            - failed_images: List of error descriptions for failed copies
        """
        copied_files = []
        failed_images = []
        
        # Apply fixed image map
        updated_matches = []
        for image_path, target_relative_path in matched_images:
            filename = os.path.basename(image_path)
            if filename in fixed_img_map:
                target_relative_path = fixed_img_map[filename]
            updated_matches.append((image_path, target_relative_path))
        
        for image_path, target_relative_path in updated_matches:
            image_path = os.path.abspath(image_path)
            
            if not os.path.isfile(image_path):
                print(f"Warning: Image file {image_path} does not exist, skipping...")
                failed_images.append(f"{os.path.basename(image_path)} (not found)")
                continue
            
            # Prevent .. paths for security
            target_relative_path = os.path.normpath(target_relative_path)
            if target_relative_path.startswith(".."):
                print(f"Warning: Skipping image with invalid target path: {target_relative_path}")
                failed_images.append(f"{os.path.basename(image_path)} (invalid target path)")
                continue
            
            try:
                # Create target directory and copy file
                target_full_path = os.path.join(self.repo_dir, target_relative_path)
                target_dir = os.path.dirname(target_full_path)
                os.makedirs(target_dir, exist_ok=True)
                
                shutil.copy2(image_path, target_full_path)
                
                if not os.path.isfile(target_full_path):
                    raise IOError(f"Failed to copy image to {target_full_path}")
                
                # Record relative path for git operations
                rel_path = os.path.relpath(target_full_path, self.repo_dir)
                if not rel_path.startswith(".."):
                    copied_files.append(rel_path)
                    print(f"✅ Copied image: {os.path.basename(image_path)} -> {rel_path}")
                else:
                    print(f"Warning: Skipping git add for image outside repo: {rel_path}")
                
            except Exception as e:
                filename = os.path.basename(image_path)
                print(f"❌ Failed to copy image {filename}: {e}")
                failed_images.append(f"{filename} (copy failed: {str(e)})")
        
        return copied_files, failed_images
