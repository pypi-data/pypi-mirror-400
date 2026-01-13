"""Shared repository cache using bare clones and worktrees.

This module manages a cache of bare git clones to avoid redundant cloning.
Worktrees are created from the bare clones for individual runs.

Directory structure:
    ~/.vibelab/repos/{host}/{owner}/{repo}.git  # bare clone
    ~/.vibelab/projects/{project}/worktrees/{result_id}  # worktree for a run
"""

from __future__ import annotations

import fcntl
import logging
import subprocess
import time
from pathlib import Path

from ..db.connection import get_repos_dir

logger = logging.getLogger(__name__)


class RepoCache:
    """Manages shared bare clones and worktrees for git repositories."""

    def __init__(self) -> None:
        self.repos_dir = get_repos_dir()

    def get_bare_clone_path(self, host: str, owner: str, repo: str) -> Path:
        """Get the path where a bare clone should be stored.

        Args:
            host: Git host (e.g., "github.com")
            owner: Repository owner
            repo: Repository name

        Returns:
            Path to the bare clone directory (e.g., ~/.vibelab/repos/github.com/owner/repo.git)
        """
        return self.repos_dir / host / owner / f"{repo}.git"

    def ensure_bare_clone(
        self, host: str, owner: str, repo: str, needed_commit: str | None = None
    ) -> Path:
        """Ensure a bare clone exists and has the needed commit.

        If the bare clone doesn't exist, creates it. If it exists, only fetches
        if the needed commit is not already present (avoids slow fetches for large repos).
        Uses file locking to prevent concurrent clone/fetch operations.

        Args:
            host: Git host (e.g., "github.com")
            owner: Repository owner
            repo: Repository name
            needed_commit: If provided, only fetch if this commit is missing locally

        Returns:
            Path to the bare clone directory
        """
        bare_path = self.get_bare_clone_path(host, owner, repo)
        lock_path = bare_path.with_suffix(".lock")

        # Ensure parent directory exists
        bare_path.parent.mkdir(parents=True, exist_ok=True)

        # Use file locking to prevent concurrent clone/fetch operations
        with open(lock_path, "w") as lock_file:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            try:
                if bare_path.exists():
                    # Bare clone exists - check if we need to fetch
                    if needed_commit and self._has_commit(bare_path, needed_commit):
                        logger.debug(f"Commit {needed_commit[:8]} already in {owner}/{repo}")
                    else:
                        # Need to fetch (commit missing or no specific commit requested)
                        start = time.time()
                        logger.debug(f"Fetching updates for {owner}/{repo}...")
                        self._fetch_bare_clone(bare_path)
                        elapsed = time.time() - start
                        logger.debug(f"Fetch completed in {elapsed:.1f}s")
                else:
                    # Create new bare clone
                    start = time.time()
                    logger.debug(f"Creating bare clone for {owner}/{repo}...")
                    self._create_bare_clone(host, owner, repo, bare_path)
                    elapsed = time.time() - start
                    logger.debug(f"Clone completed in {elapsed:.1f}s")
            finally:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)

        return bare_path

    def _has_commit(self, bare_path: Path, commit_sha: str) -> bool:
        """Check if a commit exists in the bare repository."""
        result = subprocess.run(
            ["git", "cat-file", "-t", commit_sha],
            cwd=bare_path,
            capture_output=True,
            check=False,
        )
        return result.returncode == 0

    def _create_bare_clone(self, host: str, owner: str, repo: str, bare_path: Path) -> None:
        """Create a new bare clone of the repository."""
        if host == "github.com":
            url = f"https://github.com/{owner}/{repo}.git"
        else:
            url = f"https://{host}/{owner}/{repo}.git"

        subprocess.run(
            ["git", "clone", "--bare", url, str(bare_path)],
            check=True,
            capture_output=True,
        )

    def _fetch_bare_clone(self, bare_path: Path) -> None:
        """Fetch updates for an existing bare clone."""
        subprocess.run(
            ["git", "fetch", "--all", "--prune"],
            cwd=bare_path,
            check=True,
            capture_output=True,
        )

    def create_worktree(
        self,
        host: str,
        owner: str,
        repo: str,
        commit_sha: str,
        worktree_path: Path,
    ) -> None:
        """Create a worktree from the bare clone at the specified commit.

        Args:
            host: Git host (e.g., "github.com")
            owner: Repository owner
            repo: Repository name
            commit_sha: Git commit SHA to checkout
            worktree_path: Path where the worktree should be created
        """
        # Pass the commit we need so we can skip fetch if it's already present
        bare_path = self.ensure_bare_clone(host, owner, repo, needed_commit=commit_sha)

        # Prune any stale worktrees first (cheap operation)
        subprocess.run(
            ["git", "worktree", "prune"],
            cwd=bare_path,
            check=False,
            capture_output=True,
        )

        # Ensure the worktree directory's parent exists
        worktree_path.parent.mkdir(parents=True, exist_ok=True)

        # Create worktree in detached HEAD mode at the specific commit
        # Using --detach since we're checking out a specific commit, not a branch
        start = time.time()
        subprocess.run(
            ["git", "worktree", "add", "--detach", str(worktree_path), commit_sha],
            cwd=bare_path,
            check=True,
            capture_output=True,
        )
        elapsed = time.time() - start
        logger.debug(f"Worktree created in {elapsed:.1f}s")

    def remove_worktree(self, host: str, owner: str, repo: str, worktree_path: Path) -> None:
        """Remove a worktree and clean up the bare clone's worktree registry.

        Args:
            host: Git host (e.g., "github.com")
            owner: Repository owner
            repo: Repository name
            worktree_path: Path to the worktree to remove
        """
        import shutil

        bare_path = self.get_bare_clone_path(host, owner, repo)

        # First remove the worktree from git's registry (if bare clone exists)
        if bare_path.exists():
            # Use git worktree remove if possible, otherwise just prune
            try:
                subprocess.run(
                    ["git", "worktree", "remove", "--force", str(worktree_path)],
                    cwd=bare_path,
                    check=True,
                    capture_output=True,
                )
            except subprocess.CalledProcessError:
                # Worktree may already be gone; just prune
                subprocess.run(
                    ["git", "worktree", "prune"],
                    cwd=bare_path,
                    check=False,
                    capture_output=True,
                )

        # Remove the worktree directory if it still exists
        if worktree_path.exists():
            shutil.rmtree(worktree_path, ignore_errors=True)


# Singleton instance for convenience
_repo_cache: RepoCache | None = None


def get_repo_cache() -> RepoCache:
    """Get the singleton RepoCache instance."""
    global _repo_cache
    if _repo_cache is None:
        _repo_cache = RepoCache()
    return _repo_cache
