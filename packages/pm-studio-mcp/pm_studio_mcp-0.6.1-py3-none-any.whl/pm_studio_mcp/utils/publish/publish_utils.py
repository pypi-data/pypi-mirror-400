from pm_studio_mcp.utils.publish.config import PublishConfig
from pm_studio_mcp.utils.publish.publisher import GitHubPagesPublisher
from typing import List, Optional
import os

class PublishUtils:
    @staticmethod
    def publish_html(html_file_path: str, image_paths: Optional[List[str]] = None):
        print(f"[DEBUG] Entered publish_html with html_file_path={html_file_path}, image_paths={image_paths}", flush=True)
        repo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
        print(f"[DEBUG] publish_html repo_dir resolved to: {repo_dir}", flush=True)
        config_obj = PublishConfig(
            html_file_path=html_file_path,
            repo_dir=repo_dir,
            publish_branch="reports",
            commit_message="Publish HTML report to GitHub Pages",
            image_paths=image_paths
        )
        print(f"[DEBUG] PublishConfig created", flush=True)
        publisher = GitHubPagesPublisher(config_obj)
        print(f"[DEBUG] GitHubPagesPublisher instantiated", flush=True)
        return publisher.publish()
