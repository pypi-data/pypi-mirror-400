"""Git repository operations for GitHub Pages publishing."""

import os
import subprocess
import time
from pathlib import Path
from typing import List, Tuple

from .exceptions import GitOperationError, UncommittedChangesError


class GitRepository:
    """Handles Git repository operations."""
    
    def __init__(self, repo_dir: str):
        """Initialize with repository directory."""
        self.repo_dir = repo_dir
        if not os.path.isdir(repo_dir):
            raise FileNotFoundError(f"Repository directory does not exist: {repo_dir}")

    def get_current_branch(self) -> str:
        t0 = time.time()
        print(f"[DEBUG][git_ops] Enter get_current_branch (repo_dir={self.repo_dir})", flush=True)
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.repo_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                timeout=10,  # 防止卡死
                encoding="utf-8"
            )
            print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] subprocess result: returncode={result.returncode}, stdout={result.stdout!r}, stderr={result.stderr!r}", flush=True)
            if result.returncode != 0:
                raise GitOperationError(f"git rev-parse failed: {result.stderr.strip()}")
            branch = result.stdout.strip()
            print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Current branch: {branch}", flush=True)
            return branch
        except Exception as e:
            print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Exception: {e}", flush=True)
            raise GitOperationError(f"Failed to get current branch: {e}")

    def check_uncommitted_changes(self, current_branch: str) -> None:
        t0 = time.time()
        print(f"[DEBUG][git_ops] Enter check_uncommitted_changes (branch={current_branch})", flush=True)
        try:
            print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Running: git status --porcelain", flush=True)
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                timeout=10,
                encoding="utf-8"
            )
            status_output = result.stdout.strip()
            print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] git status result: returncode={result.returncode}, stdout={status_output!r}, stderr={result.stderr!r}", flush=True)
            if result.returncode != 0:
                raise UncommittedChangesError(f"git status failed: {result.stderr.strip()}")
            if status_output:
                modified_files = []
                for line in status_output.split('\n'):
                    if line.strip():
                        filename = line[3:].strip()
                        modified_files.append(filename)
                files_list = '\n  - '.join(modified_files)
                error_msg = (
                    f"Cannot publish to GitHub Pages because your current branch '{current_branch}' has uncommitted changes.\n"
                    f"Modified files:\n  - {files_list}\n\n"
                    f"Please commit or stash your changes before running this tool:\n"
                    f"  git add .\n"
                    f"  git commit -m 'Your commit message'\n"
                    f"Or to temporarily save changes:\n"
                    f"  git stash"
                )
                print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Uncommitted changes found!", flush=True)
                raise UncommittedChangesError(error_msg)
            print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] No uncommitted changes.", flush=True)
        except Exception as e:
            print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Exception: {e}", flush=True)
            raise

    def get_branch_info(self, branch_name: str) -> Tuple[bool, bool]:
        t0 = time.time()
        print(f"[DEBUG][git_ops] Enter get_branch_info (branch={branch_name})", flush=True)
        try:
            print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Running: git branch", flush=True)
            result_local = subprocess.run(
                ["git", "branch"],
                cwd=self.repo_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                timeout=10,
                encoding="utf-8"
            )
            local_branches = result_local.stdout.strip().split('\n') if result_local.stdout else []
            local_branches = [branch.strip(' *') for branch in local_branches if branch.strip()]
            print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Local branches: {local_branches}", flush=True)
            try:
                print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Running: git branch -r", flush=True)
                result_remote = subprocess.run(
                    ["git", "branch", "-r"],
                    cwd=self.repo_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.DEVNULL,
                    timeout=10,
                    encoding="utf-8"
                )
                remote_branches = result_remote.stdout.strip().split('\n') if result_remote.stdout else []
                remote_branches = [
                    branch.strip().replace('origin/', '')
                    for branch in remote_branches
                    if branch.strip() and 'origin/' in branch
                ]
                print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Remote branches: {remote_branches}", flush=True)
            except Exception as e:
                print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] git branch -r failed: {e}", flush=True)
                remote_branches = []
            return branch_name in local_branches, branch_name in remote_branches
        except Exception as e:
            print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Exception: {e}", flush=True)
            raise GitOperationError(f"Failed to get branch info: {e}")

    def create_orphan_branch(self, branch_name: str) -> None:
        t0 = time.time()
        print(f"[DEBUG][git_ops] Enter create_orphan_branch (branch={branch_name})", flush=True)
        try:
            print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Running: git checkout --orphan {branch_name}", flush=True)
            subprocess.run(["git", "checkout", "--orphan", branch_name], cwd=self.repo_dir, stdin=subprocess.DEVNULL, timeout=20)
            print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Running: git rm -rf .", flush=True)
            subprocess.run(["git", "rm", "-rf", "."], cwd=self.repo_dir, stdin=subprocess.DEVNULL, timeout=20)
            Path(os.path.join(self.repo_dir, ".gitkeep")).touch()
            print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Running: git add .gitkeep", flush=True)
            subprocess.run(["git", "add", ".gitkeep"], cwd=self.repo_dir, stdin=subprocess.DEVNULL, timeout=10)
            print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Running: git commit -m 'init pages branch'", flush=True)
            subprocess.run(["git", "commit", "-m", "init pages branch"], cwd=self.repo_dir, stdin=subprocess.DEVNULL, timeout=10)
            print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Running: git push -u origin {branch_name}", flush=True)
            subprocess.run(["git", "push", "-u", "origin", branch_name], cwd=self.repo_dir, stdin=subprocess.DEVNULL, timeout=20)
            print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Orphan branch created and pushed.", flush=True)
        except Exception as e:
            print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Exception: {e}", flush=True)
            raise GitOperationError(f"Failed to create orphan branch '{branch_name}': {e}")

    def checkout_branch(self, branch_name: str, track_remote: bool = False) -> None:
        t0 = time.time()
        print(f"[DEBUG][git_ops] Enter checkout_branch (branch={branch_name}, track_remote={track_remote})", flush=True)
        try:
            if track_remote:
                print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Running: git checkout -b {branch_name} origin/{branch_name}", flush=True)
                subprocess.run(["git", "checkout", "-b", branch_name, f"origin/{branch_name}"], cwd=self.repo_dir, stdin=subprocess.DEVNULL, timeout=20)
            else:
                print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Running: git checkout {branch_name}", flush=True)
                subprocess.run(["git", "checkout", branch_name], cwd=self.repo_dir, stdin=subprocess.DEVNULL, timeout=20)
            print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Branch checked out.", flush=True)
        except Exception as e:
            print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Exception: {e}", flush=True)
            raise GitOperationError(f"Failed to checkout branch '{branch_name}': {e}")

    def add_and_commit_files(self, file_paths: List[str], commit_message: str) -> bool:
        t0 = time.time()
        print(f"[DEBUG][git_ops] Enter add_and_commit_files (files={file_paths}, msg={commit_message})", flush=True)
        try:
            # Add files
            for file_path in file_paths:
                abs_path = os.path.join(self.repo_dir, file_path)
                if os.path.exists(abs_path) and not file_path.startswith(".."):
                    print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Running: git add {file_path}", flush=True)
                    result_add = subprocess.run([
                        "git", "add", file_path
                    ], cwd=self.repo_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL, timeout=10, encoding="utf-8")
                    print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] git add result: returncode={result_add.returncode}, stdout={result_add.stdout!r}, stderr={result_add.stderr!r}", flush=True)
                    if result_add.returncode != 0:
                        print(f"Warning: git add failed for {file_path}: {result_add.stderr.strip()}", flush=True)
                else:
                    print(f"Warning: File {file_path} does not exist or is outside repo, skipping git add", flush=True)
            # Check if there are any staged changes
            print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Running: git status --porcelain", flush=True)
            result_status = subprocess.run([
                "git", "status", "--porcelain"
            ], cwd=self.repo_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL, timeout=10, encoding="utf-8")
            status_output = result_status.stdout.strip()
            print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] git status result: returncode={result_status.returncode}, stdout={status_output!r}, stderr={result_status.stderr!r}", flush=True)
            if result_status.returncode != 0:
                print("Warning: git status failed, aborting commit.", flush=True)
                return False
            if not status_output:
                print("Warning: No files were staged for commit. Nothing to publish.", flush=True)
                return False
            # Commit and push
            print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Running: git commit -m {commit_message}", flush=True)
            result_commit = subprocess.run([
                "git", "commit", "-m", commit_message
            ], cwd=self.repo_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL, timeout=20, encoding="utf-8")
            print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] git commit result: returncode={result_commit.returncode}, stdout={result_commit.stdout!r}, stderr={result_commit.stderr!r}", flush=True)
            if result_commit.returncode != 0:
                raise GitOperationError(f"git commit failed: {result_commit.stderr.strip()}")
            current_branch = self.get_current_branch()
            try:
                print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Running: git push origin {current_branch}", flush=True)
                result_push = subprocess.run([
                    "git", "push", "origin", current_branch
                ], cwd=self.repo_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL, timeout=30, encoding="utf-8")
                print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] git push result: returncode={result_push.returncode}, stdout={result_push.stdout!r}, stderr={result_push.stderr!r}", flush=True)
                if result_push.returncode != 0:
                    print(f"Push failed, checking for remote changes...", flush=True)
                    print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Running: git fetch origin {current_branch}", flush=True)
                    result_fetch = subprocess.run([
                        "git", "fetch", "origin", current_branch
                    ], cwd=self.repo_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL, timeout=20, encoding="utf-8")
                    print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] fetch result: returncode={result_fetch.returncode}, stdout={result_fetch.stdout!r}, stderr={result_fetch.stderr!r}", flush=True)
                    if result_fetch.returncode != 0:
                        raise GitOperationError(f"git fetch failed: {result_fetch.stderr.strip()}")
                    print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Running: git rev-parse {current_branch}", flush=True)
                    result_local = subprocess.run([
                        "git", "rev-parse", current_branch
                    ], cwd=self.repo_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL, timeout=10, encoding="utf-8")
                    local_commit = result_local.stdout.strip()
                    print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Running: git rev-parse origin/{current_branch}", flush=True)
                    result_remote = subprocess.run([
                        "git", "rev-parse", f"origin/{current_branch}"
                    ], cwd=self.repo_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL, timeout=10, encoding="utf-8")
                    remote_commit = result_remote.stdout.strip()
                    if local_commit != remote_commit:
                        print(f"Remote branch has diverged. Attempting to rebase...", flush=True)
                        print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Running: git rebase origin/{current_branch}", flush=True)
                        result_rebase = subprocess.run([
                            "git", "rebase", f"origin/{current_branch}"
                        ], cwd=self.repo_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL, timeout=30, encoding="utf-8")
                        print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] rebase result: returncode={result_rebase.returncode}, stdout={result_rebase.stdout!r}, stderr={result_rebase.stderr!r}", flush=True)
                        if result_rebase.returncode != 0:
                            raise GitOperationError(f"git rebase failed: {result_rebase.stderr.strip()}")
                        print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Running: git push origin {current_branch}", flush=True)
                        result_push2 = subprocess.run([
                            "git", "push", "origin", current_branch
                        ], cwd=self.repo_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL, timeout=30, encoding="utf-8")
                        print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] git push after rebase result: returncode={result_push2.returncode}, stdout={result_push2.stdout!r}, stderr={result_push2.stderr!r}", flush=True)
                        if result_push2.returncode != 0:
                            raise GitOperationError(f"git push after rebase failed: {result_push2.stderr.strip()}")
                        print(f"Successfully rebased and pushed to {current_branch}", flush=True)
                    else:
                        raise GitOperationError(f"git push failed: {result_push.stderr.strip()}")
            except Exception as push_error:
                print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Exception during push: {push_error}", flush=True)
                raise push_error
            return True
        except Exception as e:
            print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Exception: {e}", flush=True)
            raise GitOperationError(f"Failed to commit and push files: {e}")

    def get_github_pages_url(self, file_name: str) -> str:
        t0 = time.time()
        print(f"[DEBUG][git_ops] Enter get_github_pages_url (file_name={file_name})", flush=True)
        try:
            print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Running: git config --get remote.origin.url", flush=True)
            result_remote = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                cwd=self.repo_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                timeout=10,
                encoding="utf-8"
            )
            print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] git config result: returncode={result_remote.returncode}, stdout={result_remote.stdout!r}, stderr={result_remote.stderr!r}", flush=True)
            if result_remote.returncode != 0:
                raise GitOperationError(f"git config failed: {result_remote.stderr.strip()}")
            remote_url = result_remote.stdout.strip()
            print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] remote_url: {remote_url}", flush=True)
            if remote_url.endswith(".git"):
                remote_url = remote_url[:-4]
            if remote_url.startswith("git@github.com:"):
                remote_url = remote_url.replace("git@github.com:", "https://github.com/")
            elif not remote_url.startswith("https://github.com/"):
                raise GitOperationError(f"Unknown remote url: {remote_url}")
            user_repo = remote_url.split("github.com/")[-1]
            url = f"https://{user_repo.split('/')[0]}.github.io/{user_repo.split('/')[1]}/{file_name}"
            print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] github pages url: {url}", flush=True)
            return url
        except Exception as e:
            print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Exception: {e}", flush=True)
            raise GitOperationError(f"Failed to get GitHub Pages URL: {e}")

    def fetch_and_sync_branch(self, branch_name: str) -> None:
        t0 = time.time()
        print(f"[DEBUG][git_ops] Enter fetch_and_sync_branch (branch={branch_name})", flush=True)
        try:
            print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Running: git fetch origin {branch_name}", flush=True)
            result_fetch = subprocess.run(
                ["git", "fetch", "origin", branch_name],
                cwd=self.repo_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                timeout=20,
                encoding="utf-8"
            )
            print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] fetch result: returncode={result_fetch.returncode}, stdout={result_fetch.stdout!r}, stderr={result_fetch.stderr!r}", flush=True)
            if result_fetch.returncode != 0:
                raise GitOperationError(f"git fetch failed: {result_fetch.stderr.strip()}")

            print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Running: git rev-parse {branch_name}", flush=True)
            result_local = subprocess.run(
                ["git", "rev-parse", branch_name],
                cwd=self.repo_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                timeout=10,
                encoding="utf-8"
            )
            local_commit = result_local.stdout.strip()
            print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Running: git rev-parse origin/{branch_name}", flush=True)
            result_remote = subprocess.run(
                ["git", "rev-parse", f"origin/{branch_name}"],
                cwd=self.repo_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                timeout=10,
                encoding="utf-8"
            )
            remote_commit = result_remote.stdout.strip()
            if local_commit != remote_commit:
                print(f"Local branch {branch_name} has diverged from remote. Checking merge strategy...", flush=True)
                
                # Check if local is ahead, behind, or diverged
                print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Running: git merge-base {branch_name} origin/{branch_name}", flush=True)
                result_base = subprocess.run(
                    ["git", "merge-base", branch_name, f"origin/{branch_name}"],
                    cwd=self.repo_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.DEVNULL,
                    timeout=10,
                    encoding="utf-8"
                )
                
                if result_base.returncode == 0:
                    base_commit = result_base.stdout.strip()
                    if base_commit == local_commit:
                        print(f"Local branch {branch_name} is behind remote. Fast-forwarding...", flush=True)
                        print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Running: git merge --ff-only origin/{branch_name}", flush=True)
                        result_merge = subprocess.run(
                            ["git", "merge", "--ff-only", f"origin/{branch_name}"],
                            cwd=self.repo_dir,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            stdin=subprocess.DEVNULL,
                            timeout=20,
                            encoding="utf-8"
                        )
                        print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] merge result: returncode={result_merge.returncode}, stdout={result_merge.stdout!r}, stderr={result_merge.stderr!r}", flush=True)
                        if result_merge.returncode != 0:
                            raise GitOperationError(f"git merge failed: {result_merge.stderr.strip()}")
                        print(f"Successfully fast-forwarded {branch_name} to match remote", flush=True)
                    elif base_commit == remote_commit:
                        print(f"Local branch {branch_name} is ahead of remote. No sync needed.", flush=True)
                    else:
                        # Handle branch divergence more proactively
                        print(f"Local branch {branch_name} has diverged from remote. Attempting to resolve...", flush=True)
                        try:
                            if branch_name == "reports":
                                # For reports branch, use force sync strategy to ensure clean state
                                print(f"Using force sync strategy for reports branch...", flush=True)
                                print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Running: git reset --hard origin/{branch_name}", flush=True)
                                result_reset = subprocess.run([
                                    "git", "reset", "--hard", f"origin/{branch_name}"
                                ], cwd=self.repo_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                  stdin=subprocess.DEVNULL, timeout=10, encoding="utf-8")
                                print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] reset result: returncode={result_reset.returncode}, stdout={result_reset.stdout!r}, stderr={result_reset.stderr!r}", flush=True)
                                if result_reset.returncode != 0:
                                    raise GitOperationError(f"git reset failed: {result_reset.stderr.strip()}")
                                print(f"Successfully synced {branch_name} with remote (local changes discarded)", flush=True)
                            else:
                                # For other branches, attempt rebase first
                                print(f"Attempting to rebase {branch_name} onto origin/{branch_name}...", flush=True)
                                print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Running: git rebase origin/{branch_name}", flush=True)
                                result_rebase = subprocess.run([
                                    "git", "rebase", f"origin/{branch_name}"
                                ], cwd=self.repo_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                  stdin=subprocess.DEVNULL, timeout=30, encoding="utf-8")
                                print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] rebase result: returncode={result_rebase.returncode}, stdout={result_rebase.stdout!r}, stderr={result_rebase.stderr!r}", flush=True)
                                if result_rebase.returncode != 0:
                                    print(f"Rebase failed, falling back to force sync...", flush=True)
                                    print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Running: git reset --hard origin/{branch_name}", flush=True)
                                    result_reset = subprocess.run([
                                        "git", "reset", "--hard", f"origin/{branch_name}"
                                    ], cwd=self.repo_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                      stdin=subprocess.DEVNULL, timeout=10, encoding="utf-8")
                                    if result_reset.returncode != 0:
                                        raise GitOperationError(f"git reset failed: {result_reset.stderr.strip()}")
                                    print(f"Successfully synced {branch_name} with remote (local changes discarded)", flush=True)
                                else:
                                    print(f"Successfully rebased {branch_name} onto remote", flush=True)
                        except Exception as e:
                            raise GitOperationError(f"Failed to resolve branch divergence for {branch_name}: {e}")
                else:
                    print(f"Could not determine merge base. Continuing with local branch state...", flush=True)
            else:
                print(f"Branch {branch_name} is already up to date with remote", flush=True)
        except Exception as e:
            print(f"[DEBUG][git_ops][T+{time.time()-t0:.2f}s] Exception: {e}", flush=True)
            raise GitOperationError(f"Failed to fetch and sync branch '{branch_name}': {e}")
