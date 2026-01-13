"""Tests for Hacker News platform."""
import pytest


class TestHackernews:
    """Test Hacker News platform"""

    def test_hackernews(self, sl):
        """Test Hacker News platform"""
        profile_id = "pg"
        assert sl.detect_platform(f"https://news.ycombinator.com/user?id={profile_id}") == "hackernews"
        assert sl.is_valid("hackernews", f"https://news.ycombinator.com/user?id={profile_id}") is True
        assert sl.sanitize("hackernews", f"https://news.ycombinator.com/user?id={profile_id}") == f"https://news.ycombinator.com/user?id={profile_id}"
        # Test direct username
        assert sl.is_valid("hackernews", profile_id) is True
        assert sl.sanitize("hackernews", profile_id) == f"https://news.ycombinator.com/user?id={profile_id}"

