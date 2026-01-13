"""Tests for GitHub platform."""
import pytest


class TestGithub:
    """Test GitHub platform"""

    def test_github(self, sl):
        """Test GitHub platform"""
        profile_id = "ysskrishna"
        assert sl.detect_platform(f"https://github.com/{profile_id}") == "github"
        assert sl.is_valid("github", f"https://github.com/{profile_id}") is True
        assert sl.sanitize("github", f"https://github.com/{profile_id}") == f"https://github.com/{profile_id}"
        # Test direct username
        assert sl.is_valid("github", profile_id) is True
        assert sl.sanitize("github", profile_id) == f"https://github.com/{profile_id}"

