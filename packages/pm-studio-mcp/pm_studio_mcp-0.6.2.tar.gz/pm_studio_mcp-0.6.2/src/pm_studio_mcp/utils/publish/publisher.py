"""Main GitHub Pages publisher class."""

import os
import shutil
from typing import List, Optional

from .config import PublishConfig
from .exceptions import GitOperationError, PublishError
from .git_ops import GitRepository
from .html_processor import HtmlProcessor
from .image_manager import ImageManager


class GitHubPagesPublisher:
    """Main class for publishing HTML files to GitHub Pages."""
    
    def __init__(self, config: PublishConfig):
        """Initialize publisher with configuration."""
        self.config = config
        self.git_repo = GitRepository(config.repo_dir)
        self.html_processor = HtmlProcessor()
        self.image_manager = ImageManager(config.repo_dir)
    
    def publish(self) -> Optional[str]:
        """Publish HTML file and images to GitHub Pages.
        
        Returns:
            GitHub Pages URL where the file can be accessed, or None if failed
            
        Raises:
            PublishError: If publishing fails
        """
        import time
        file_name = os.path.basename(self.config.html_file_path)
        current_branch = self.git_repo.get_current_branch()
        print(f"[DEBUG] Starting publish: file_name={file_name}, current_branch={current_branch}", flush=True)
        t0 = time.time()
        try:
            print(f"[DEBUG] [T+{time.time()-t0:.2f}s] Checking for uncommitted changes...", flush=True)
            self.git_repo.check_uncommitted_changes(current_branch)
            print(f"[DEBUG] [T+{time.time()-t0:.2f}s] Uncommitted changes check passed.", flush=True)

            print(f"[DEBUG] [T+{time.time()-t0:.2f}s] Setting up publish branch: {self.config.publish_branch}", flush=True)
            self._setup_publish_branch()
            print(f"[DEBUG] [T+{time.time()-t0:.2f}s] Switched to branch: {self.config.publish_branch}", flush=True)

            dst = os.path.join(self.config.repo_dir, file_name)
            print(f"[DEBUG] [T+{time.time()-t0:.2f}s] Copying HTML file to {dst}", flush=True)
            shutil.copy2(self.config.html_file_path, dst)
            print(f"[DEBUG] [T+{time.time()-t0:.2f}s] HTML file copied.", flush=True)

            copied_files = [file_name]
            if self.config.image_paths:
                print(f"[DEBUG] [T+{time.time()-t0:.2f}s] Processing images: {self.config.image_paths}", flush=True)
                image_files = self._process_images(dst)
                copied_files.extend(image_files)
                print(f"[DEBUG] [T+{time.time()-t0:.2f}s] Images processed: {image_files}", flush=True)

            if copied_files:
                print(f"[DEBUG] [T+{time.time()-t0:.2f}s] Adding and committing files: {copied_files}", flush=True)
                success = self.git_repo.add_and_commit_files(copied_files, self.config.commit_message)
                print(f"[DEBUG] [T+{time.time()-t0:.2f}s] Commit and push result: {success}", flush=True)
                if success:
                    print(f"✅ Successfully pushed {len(copied_files)} file(s) to {self.config.publish_branch} branch", flush=True)
                else:
                    print("[DEBUG] No files were committed.", flush=True)
                    return None
            else:
                print("Warning: No files to publish", flush=True)
                return None

            print(f"[DEBUG] [T+{time.time()-t0:.2f}s] Getting GitHub Pages URL for {file_name}", flush=True)
            url = self.git_repo.get_github_pages_url(file_name)
            print(f"[DEBUG] [T+{time.time()-t0:.2f}s] Publish complete. URL: {url}", flush=True)
            return url
        except GitOperationError as e:
            print(f"❌ Git operation failed: {e}", flush=True)
            raise PublishError(f"Failed to publish to GitHub Pages: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}", flush=True)
            raise PublishError(f"Unexpected error during publishing: {e}")
        finally:
            try:
                print(f"[DEBUG] [T+{time.time()-t0:.2f}s] Switching back to original branch: {current_branch}", flush=True)
                self.git_repo.checkout_branch(current_branch)
                print(f"[DEBUG] [T+{time.time()-t0:.2f}s] Switched back to {current_branch}", flush=True)
            except Exception as e:
                print(f"[DEBUG] Failed to switch back to {current_branch}: {e}", flush=True)
                pass
    
    def _setup_publish_branch(self) -> None:
        """Setup the publish branch (create if needed, checkout)."""
        branch_exists_locally, branch_exists_remotely = self.git_repo.get_branch_info(self.config.publish_branch)
        
        if not branch_exists_locally and not branch_exists_remotely:
            self.git_repo.create_orphan_branch(self.config.publish_branch)
        elif branch_exists_remotely and not branch_exists_locally:
            self.git_repo.checkout_branch(self.config.publish_branch, track_remote=True)
        else:
            self.git_repo.checkout_branch(self.config.publish_branch)
            
            # If branch exists both locally and remotely, ensure we're up to date
            if branch_exists_remotely:
                try:
                    print(f"Fetching latest changes for {self.config.publish_branch} branch...")
                    self.git_repo.fetch_and_sync_branch(self.config.publish_branch)
                except Exception as e:
                    print(f"Warning: Could not fetch remote changes: {e}")
                    print("Continuing with local branch state...")
    
    def _process_images(self, html_dst_path: str) -> List[str]:
        """Process and copy images, return list of copied file paths.
        
        Args:
            html_dst_path: Path to the copied HTML file in the repository
            
        Returns:
            List of relative paths of successfully copied image files
        """
        # Fix HTML image paths
        _, fixed_img_map = self.html_processor.fix_image_paths(html_dst_path)
        
        # Parse HTML for image references
        html_image_refs = self.html_processor.parse_image_references(html_dst_path)
        print(f"Found {len(html_image_refs)} image references in HTML: {list(html_image_refs.values())}")
        
        # Match images to HTML paths
        matched_images = self.image_manager.match_images_to_html_paths(self.config.image_paths, html_image_refs)
        
        # Copy images
        copied_files, failed_images = self.image_manager.copy_images(matched_images, fixed_img_map)
        
        # Report failures
        if failed_images:
            print(f"\nWarning: {len(failed_images)} image(s) failed to process:")
            for failed in failed_images:
                print(f"  - {failed}")
            print("The HTML file will still be published, but some images may be missing.")
        
        return copied_files
