"""Tests for GitLab platform."""
import pytest


class TestGitlab:
    """Test GitLab platform"""

    def test_gitlab(self, sl):
        """Test GitLab platform"""
        profile_id = "ysskrishna"
        assert sl.detect_platform(f"https://gitlab.com/{profile_id}") == "gitlab"
        assert sl.is_valid("gitlab", f"https://gitlab.com/{profile_id}") is True
        assert sl.sanitize("gitlab", f"https://gitlab.com/{profile_id}") == f"https://gitlab.com/{profile_id}"
        # Test direct username
        assert sl.is_valid("gitlab", profile_id) is True
        assert sl.sanitize("gitlab", profile_id) == f"https://gitlab.com/{profile_id}"

