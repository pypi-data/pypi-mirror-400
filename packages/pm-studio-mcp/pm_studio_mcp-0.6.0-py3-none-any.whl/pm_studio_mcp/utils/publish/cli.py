#!/usr/bin/env python3
"""Command-line interface for GitHub Pages publisher."""

import os
import sys
import argparse
import tempfile

# Add the src directory to Python path when running as script
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.abspath(os.path.join(current_dir, '../../..'))
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

from pm_studio_mcp.utils.publish import PublishConfig, GitHubPagesPublisher


def main():
    """Command-line interface for the GitHub Pages publisher."""
    parser = argparse.ArgumentParser(
        description="Publish a local HTML file to reports branch and print the GitHub Pages URL."
    )
    parser.add_argument("html_file_path", nargs="?", help="Path to the local HTML file to publish")
    parser.add_argument(
        "--repo_dir", 
        default=os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')),
        help="Path to the git repository root (default: project root)"
    )
    parser.add_argument("--branch", default="reports", help="Publish branch (default: reports)")
    parser.add_argument("--message", default="Publish HTML report to GitHub Pages", help="Commit message")
    parser.add_argument("--images", nargs="*", help="Optional list of image file paths to upload to assets/images/")
    parser.add_argument("--test", action="store_true", help="Run a test publishing with a generated HTML and image")
    
    args = parser.parse_args()

    if args.test:
        # Create a temp HTML file and a temp image
        with tempfile.TemporaryDirectory() as tmpdir:
            html_path = os.path.join(tmpdir, "test_report.html")
            img_path = os.path.join(tmpdir, "test_image.png")
            
            # Write a simple HTML referencing the image
            with open(html_path, "w", encoding="utf-8") as f:
                f.write('<html><body><h1>Test Report</h1><img src="test_image.png" /></body></html>')
            
            # Create a dummy PNG file
            with open(img_path, "wb") as f:
                f.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0bIDATx\x9cc``\x00\x00\x00\x02\x00\x01\xe2!\xbc3\x00\x00\x00\x00IEND\xaeB`\x82")
            
            print(f"[TEST] Created temp HTML: {html_path}")
            print(f"[TEST] Created temp image: {img_path}")
            
            try:
                config = PublishConfig(
                    html_file_path=html_path,
                    repo_dir=args.repo_dir,
                    publish_branch=args.branch,
                    commit_message="[TEST] Publish HTML report to GitHub Pages",
                    image_paths=[img_path]
                )
                publisher = GitHubPagesPublisher(config)
                url = publisher.publish()
                print(f"[TEST] Published! Access URL: {url}")
            except Exception as e:
                print(f"[TEST] Failed: {e}")
            sys.exit(0)

    if not args.html_file_path:
        parser.error("html_file_path is required unless --test is specified")

    try:
        config = PublishConfig(
            html_file_path=args.html_file_path,
            repo_dir=args.repo_dir,
            publish_branch=args.branch,
            commit_message=args.message,
            image_paths=args.images
        )
        publisher = GitHubPagesPublisher(config)
        url = publisher.publish()
        print(f"Published! Access URL: {url}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
