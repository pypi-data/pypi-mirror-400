"""Tests for X (formerly Twitter) platform."""
import pytest


class TestX:
    """Test X platform"""

    def test_x(self, sl):
        """Test X (formerly Twitter) platform"""
        profile_id = "ysskrishna"
        assert sl.detect_platform(f"https://x.com/{profile_id}") == "x"
        assert sl.is_valid("x", f"https://x.com/{profile_id}") is True
        assert sl.sanitize("x", f"https://x.com/{profile_id}") == f"https://x.com/{profile_id}"
        # Test direct username (with and without @)
        assert sl.is_valid("x", profile_id) is True
        assert sl.is_valid("x", f"@{profile_id}") is True
        assert sl.sanitize("x", profile_id) == f"https://x.com/{profile_id}"
        assert sl.sanitize("x", f"@{profile_id}") == f"https://x.com/{profile_id}"

    def test_x_twitter_urls(self, sl):
        """Test X platform with Twitter URLs (X handles both x.com and twitter.com)"""
        profile_id = "ysskrishna"
        # Twitter URLs should be detected as X platform
        assert sl.detect_platform(f"https://twitter.com/{profile_id}") == "x"
        assert sl.detect_platform(f"https://mobile.twitter.com/{profile_id}") == "x"
        assert sl.is_valid("x", f"https://twitter.com/{profile_id}") is True
        assert sl.is_valid("x", f"https://mobile.twitter.com/{profile_id}") is True
        # Twitter URLs should be sanitized to x.com
        assert sl.sanitize("x", f"https://twitter.com/{profile_id}") == f"https://x.com/{profile_id}"
        assert sl.sanitize("x", f"https://mobile.twitter.com/{profile_id}") == f"https://x.com/{profile_id}"

