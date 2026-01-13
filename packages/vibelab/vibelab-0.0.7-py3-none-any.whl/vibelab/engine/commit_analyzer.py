"""Analyze GitHub commits to extract context for scenario generation."""

import logging
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .repo_cache import get_repo_cache

logger = logging.getLogger(__name__)


@dataclass
class CommitInfo:
    """Information about a commit."""

    owner: str
    repo: str
    commit_sha: str
    parent_sha: str
    commit_message: str
    commit_author: str | None = None
    commit_date: str | None = None


@dataclass
class PRInfo:
    """Information about an associated PR."""

    number: int
    title: str
    body: str


def _ensure_repo_cached(owner: str, repo: str, needed_commit: str | None = None) -> Path:
    """Ensure repo is cloned (bare) in cache, return path.

    Uses the shared RepoCache for consistent caching across the system.

    Args:
        owner: Repository owner
        repo: Repository name
        needed_commit: If provided, only fetch if this commit is missing

    Returns:
        Path to the bare clone directory
    """
    cache = get_repo_cache()
    return cache.ensure_bare_clone("github.com", owner, repo, needed_commit=needed_commit)


def _fetch_commit_if_needed(repo_path: Path, commit_sha: str) -> None:
    """Fetch a specific commit if not available locally."""
    # Check if commit exists
    result = subprocess.run(
        ["git", "cat-file", "-t", commit_sha],
        cwd=repo_path,
        capture_output=True,
    )

    if result.returncode != 0:
        # Commit not found, try to fetch it
        logger.info(f"Fetching commit {commit_sha[:8]}...")
        subprocess.run(
            ["git", "fetch", "origin", commit_sha],
            cwd=repo_path,
            check=True,
            capture_output=True,
            timeout=60,
        )


def parse_commit_url(url: str) -> tuple[str, str, str] | None:
    """Parse a GitHub commit URL into (owner, repo, commit_sha).

    Supports formats:
    - https://github.com/owner/repo/commit/abc123
    - https://github.com/owner/repo/commit/abc123def456...
    - owner/repo@abc123
    - owner/repo@main (will need resolution)
    """
    # Full URL format
    url_match = re.match(
        r"https?://github\.com/([^/]+)/([^/]+)/commit/([a-f0-9]+)",
        url,
        re.IGNORECASE,
    )
    if url_match:
        return url_match.group(1), url_match.group(2), url_match.group(3)

    # Short format: owner/repo@sha
    short_match = re.match(r"([^/@]+)/([^/@]+)@([a-f0-9]+)", url, re.IGNORECASE)
    if short_match:
        return short_match.group(1), short_match.group(2), short_match.group(3)

    return None


def fetch_commit_info(owner: str, repo: str, commit_sha: str) -> CommitInfo:
    """Fetch commit information using cached repo.

    Returns CommitInfo with parent SHA, message, author, etc.
    """
    try:
        # Ensure repo is cached with the specific commit we need
        repo_path = _ensure_repo_cached(owner, repo, needed_commit=commit_sha)

        # Fetch specific commit if needed (fallback for edge cases)
        _fetch_commit_if_needed(repo_path, commit_sha)

        # Get commit message
        message_result = subprocess.run(
            ["git", "log", "-1", "--format=%B", commit_sha],
            cwd=repo_path,
            check=True,
            capture_output=True,
            text=True,
        )
        commit_message = message_result.stdout.strip()

        # Get commit author
        author_result = subprocess.run(
            ["git", "log", "-1", "--format=%an <%ae>", commit_sha],
            cwd=repo_path,
            check=True,
            capture_output=True,
            text=True,
        )
        commit_author = author_result.stdout.strip() or None

        # Get commit date
        date_result = subprocess.run(
            ["git", "log", "-1", "--format=%ai", commit_sha],
            cwd=repo_path,
            check=True,
            capture_output=True,
            text=True,
        )
        commit_date = date_result.stdout.strip() or None

        # Get parent SHA (first parent)
        parent_result = subprocess.run(
            ["git", "rev-parse", f"{commit_sha}^"],
            cwd=repo_path,
            check=False,
            capture_output=True,
            text=True,
        )
        if parent_result.returncode == 0:
            parent_sha = parent_result.stdout.strip()
        else:
            # Check if this is an initial commit (no parent)
            parent_count_result = subprocess.run(
                ["git", "rev-list", "--count", "--parents", "-n", "1", commit_sha],
                cwd=repo_path,
                check=False,
                capture_output=True,
                text=True,
            )
            # rev-list --parents outputs: sha [parent1] [parent2]...
            # Count the number of SHAs in output
            if parent_count_result.returncode == 0:
                parts = parent_count_result.stdout.strip().split()
                if len(parts) == 1:
                    # Only the commit SHA, no parents - initial commit
                    logger.info(f"Commit {commit_sha[:8]} is an initial commit")
                    parent_sha = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
                else:
                    # Has parents but rev-parse failed - shouldn't happen
                    raise ValueError(
                        f"Could not resolve parent for {commit_sha}: {parent_result.stderr}"
                    )
            else:
                logger.warning(f"Could not verify parent for {commit_sha}, assuming initial")
                parent_sha = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"

        return CommitInfo(
            owner=owner,
            repo=repo,
            commit_sha=commit_sha,
            parent_sha=parent_sha,
            commit_message=commit_message,
            commit_author=commit_author,
            commit_date=commit_date,
        )
    except subprocess.CalledProcessError as e:
        stderr = e.stderr
        if isinstance(stderr, bytes):
            stderr = stderr.decode()
        error_msg = stderr or str(e)
        logger.error(f"Failed to fetch commit info: {error_msg}")
        raise ValueError(f"Failed to fetch commit {commit_sha} from {owner}/{repo}: {error_msg}")
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout fetching commit info for {commit_sha}")
        raise ValueError(f"Timeout fetching commit {commit_sha} from {owner}/{repo}")


def fetch_commit_diff(owner: str, repo: str, commit_sha: str, max_lines: int = 2000) -> str:
    """Fetch the diff for a commit using cached repo.

    Args:
        owner: Repository owner
        repo: Repository name
        commit_sha: Commit SHA
        max_lines: Maximum lines to return (truncate if larger)

    Returns:
        Diff string (may be truncated)
    """
    try:
        # Ensure repo is cached with the specific commit we need
        repo_path = _ensure_repo_cached(owner, repo, needed_commit=commit_sha)

        # Fetch specific commit if needed (fallback for edge cases)
        _fetch_commit_if_needed(repo_path, commit_sha)

        # Get diff directly from bare repo
        diff_result = subprocess.run(
            ["git", "show", "--format=", commit_sha],
            cwd=repo_path,
            check=True,
            capture_output=True,
            text=True,
        )
        diff = diff_result.stdout

        # Truncate if too large
        lines = diff.split("\n")
        if len(lines) > max_lines:
            diff = "\n".join(lines[:max_lines])
            diff += f"\n... (truncated, {len(lines) - max_lines} more lines)"

        return diff
    except subprocess.CalledProcessError as e:
        stderr = e.stderr
        if isinstance(stderr, bytes):
            stderr = stderr.decode()
        error_msg = stderr or str(e)
        logger.error(f"Failed to fetch commit diff: {error_msg}")
        raise ValueError(f"Failed to fetch diff for {commit_sha} from {owner}/{repo}: {error_msg}")
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout fetching diff for {commit_sha}")
        raise ValueError(f"Timeout fetching diff for {commit_sha} from {owner}/{repo}")


def fetch_pr_for_commit(owner: str, repo: str, commit_sha: str) -> PRInfo | None:
    """Attempt to find the PR associated with a commit using GitHub API.

    This is best-effort - returns None if:
    - GitHub API key is not configured
    - PR cannot be found
    - API call fails

    Args:
        owner: Repository owner
        repo: Repository name
        commit_sha: Commit SHA

    Returns:
        PRInfo if found, None otherwise
    """
    api_key = os.environ.get("GITHUB_API_KEY") or os.environ.get("GITHUB_TOKEN")
    if not api_key:
        logger.debug("No GITHUB_API_KEY or GITHUB_TOKEN found, skipping PR lookup")
        return None

    try:
        import requests

        # Find PRs that contain this commit
        url = f"https://api.github.com/repos/{owner}/{repo}/commits/{commit_sha}/pulls"
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {api_key}",
        }
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 404:
            # Commit not found or no PRs
            return None

        response.raise_for_status()
        prs = response.json()

        if not prs or len(prs) == 0:
            return None

        # Use the first PR (most recent)
        pr = prs[0]
        pr_number = pr["number"]

        # Fetch full PR details to get the complete body/description
        # The /commits/{sha}/pulls endpoint may not return full PR body
        try:
            pr_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
            pr_response = requests.get(pr_url, headers=headers, timeout=10)
            if pr_response.status_code == 200:
                full_pr = pr_response.json()
                pr_body = full_pr.get("body") or ""
                pr_title = full_pr.get("title") or ""
            else:
                # Fallback to data from commits endpoint
                pr_body = pr.get("body", "") or ""
                pr_title = pr.get("title", "") or ""
        except Exception as e:
            logger.warning(f"Failed to fetch full PR details for {pr_number}: {e}, using summary")
            pr_body = pr.get("body", "") or ""
            pr_title = pr.get("title", "") or ""

        return PRInfo(
            number=pr_number,
            title=pr_title,
            body=pr_body,
        )
    except ImportError:
        logger.debug("requests library not available, skipping PR lookup")
        return None
    except Exception as e:
        logger.warning(f"Failed to fetch PR for commit {commit_sha}: {e}")
        return None


def summarize_diff_if_large(diff: str, max_lines: int = 500) -> str:
    """Truncate and summarize a large diff.

    If diff exceeds max_lines, truncate and add a summary note.
    """
    lines = diff.split("\n")
    if len(lines) <= max_lines:
        return diff

    truncated = "\n".join(lines[:max_lines])
    truncated += f"\n\n... (diff truncated, {len(lines) - max_lines} more lines)"
    return truncated
