"""Unit tests for commit analyzer functionality."""

import unittest
from unittest.mock import MagicMock, patch

from vibelab.engine.commit_analyzer import (
    PRInfo,
    fetch_pr_for_commit,
    parse_commit_url,
)


class TestParseCommitUrl(unittest.TestCase):
    """Tests for parse_commit_url function."""

    def test_parse_standard_github_url(self):
        """Test parsing standard GitHub commit URL."""
        url = "https://github.com/owner/repo/commit/abc123def456"
        result = parse_commit_url(url)
        self.assertIsNotNone(result)
        owner, repo, sha = result
        self.assertEqual(owner, "owner")
        self.assertEqual(repo, "repo")
        self.assertEqual(sha, "abc123def456")

    def test_parse_short_sha(self):
        """Test parsing URL with short SHA."""
        url = "https://github.com/myorg/myrepo/commit/abc123"
        result = parse_commit_url(url)
        self.assertIsNotNone(result)
        owner, repo, sha = result
        self.assertEqual(sha, "abc123")

    def test_parse_full_sha(self):
        """Test parsing URL with full 40-char SHA."""
        full_sha = "a" * 40
        url = f"https://github.com/owner/repo/commit/{full_sha}"
        result = parse_commit_url(url)
        self.assertIsNotNone(result)
        owner, repo, sha = result
        self.assertEqual(sha, full_sha)

    def test_parse_invalid_url(self):
        """Test parsing invalid URL returns None."""
        invalid_urls = [
            "https://github.com/owner/repo",  # No commit path
            "https://gitlab.com/owner/repo/commit/abc123",  # Not GitHub
            "not a url",
        ]
        for url in invalid_urls:
            result = parse_commit_url(url)
            self.assertIsNone(result, f"Should return None for: {url}")


class TestFetchPrForCommit(unittest.TestCase):
    """Tests for fetch_pr_for_commit function."""

    @patch.dict("os.environ", {"GITHUB_TOKEN": "", "GITHUB_API_KEY": ""}, clear=True)
    def test_no_api_key_returns_none(self):
        """Test that missing API key returns None."""
        result = fetch_pr_for_commit("owner", "repo", "abc123")
        self.assertIsNone(result)

    @patch.dict("os.environ", {"GITHUB_TOKEN": "test-token"})
    @patch("requests.get")
    def test_fetches_full_pr_body(self, mock_get):
        """Test that full PR body is fetched from PR endpoint."""
        # Mock commits/{sha}/pulls response (may have truncated body)
        commits_response = MagicMock()
        commits_response.status_code = 200
        commits_response.json.return_value = [
            {
                "number": 42,
                "title": "PR Title from commits endpoint",
                "body": "Short body",  # May be truncated
            }
        ]
        commits_response.raise_for_status = MagicMock()

        # Mock pulls/{number} response (full body)
        pr_response = MagicMock()
        pr_response.status_code = 200
        pr_response.json.return_value = {
            "number": 42,
            "title": "Full PR Title",
            "body": "This is the full PR description with all the details.",
        }

        # Configure get to return different responses based on URL
        def side_effect(url, **kwargs):
            if "/pulls/42" in url:
                return pr_response
            return commits_response

        mock_get.side_effect = side_effect

        result = fetch_pr_for_commit("owner", "repo", "abc123")

        self.assertIsNotNone(result)
        self.assertIsInstance(result, PRInfo)
        self.assertEqual(result.number, 42)
        self.assertEqual(result.title, "Full PR Title")
        self.assertEqual(
            result.body, "This is the full PR description with all the details."
        )

    @patch.dict("os.environ", {"GITHUB_TOKEN": "test-token"})
    @patch("requests.get")
    def test_falls_back_to_commits_endpoint_body(self, mock_get):
        """Test fallback to commits endpoint body if PR fetch fails."""
        # Mock commits/{sha}/pulls response
        commits_response = MagicMock()
        commits_response.status_code = 200
        commits_response.json.return_value = [
            {
                "number": 42,
                "title": "PR Title",
                "body": "Fallback body from commits endpoint",
            }
        ]
        commits_response.raise_for_status = MagicMock()

        # Mock pulls/{number} response - fails
        pr_response = MagicMock()
        pr_response.status_code = 404

        def side_effect(url, **kwargs):
            if "/pulls/42" in url:
                return pr_response
            return commits_response

        mock_get.side_effect = side_effect

        result = fetch_pr_for_commit("owner", "repo", "abc123")

        self.assertIsNotNone(result)
        self.assertEqual(result.body, "Fallback body from commits endpoint")

    @patch.dict("os.environ", {"GITHUB_TOKEN": "test-token"})
    @patch("requests.get")
    def test_handles_no_pr_found(self, mock_get):
        """Test handling when no PR is found for commit."""
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = []  # No PRs
        response.raise_for_status = MagicMock()

        mock_get.return_value = response

        result = fetch_pr_for_commit("owner", "repo", "abc123")
        self.assertIsNone(result)

    @patch.dict("os.environ", {"GITHUB_TOKEN": "test-token"})
    @patch("requests.get")
    def test_handles_commit_not_found(self, mock_get):
        """Test handling when commit is not found (404)."""
        response = MagicMock()
        response.status_code = 404

        mock_get.return_value = response

        result = fetch_pr_for_commit("owner", "repo", "nonexistent")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()

