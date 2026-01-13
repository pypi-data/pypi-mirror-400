"""Tests for Tumblr platform."""
import pytest


class TestTumblr:
    """Test Tumblr platform"""

    def test_tumblr(self, sl):
        """Test Tumblr platform with subdomain"""
        profile_id = "ysskrishna"
        assert sl.detect_platform(f"https://{profile_id}.tumblr.com") == "tumblr"
        assert sl.is_valid("tumblr", f"https://{profile_id}.tumblr.com") is True
        assert sl.sanitize("tumblr", f"https://{profile_id}.tumblr.com") == f"https://tumblr.com/{profile_id}"
        # Test direct username
        assert sl.is_valid("tumblr", profile_id) is True
        assert sl.sanitize("tumblr", profile_id) == f"https://tumblr.com/{profile_id}"

    def test_tumblr_blog_path(self, sl):
        """Test Tumblr /blog/ path"""
        profile_id = "ysskrishna"
        assert sl.detect_platform(f"https://tumblr.com/blog/{profile_id}") == "tumblr"
        assert sl.is_valid("tumblr", f"https://tumblr.com/blog/{profile_id}") is True
        assert sl.sanitize("tumblr", f"https://tumblr.com/blog/{profile_id}") == f"https://tumblr.com/{profile_id}"

