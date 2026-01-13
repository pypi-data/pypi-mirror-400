"""Tests for Bluesky platform."""
import pytest


class TestBluesky:
    """Test Bluesky platform"""

    def test_bluesky(self, sl):
        """Test Bluesky platform"""
        profile_id = "ysskrishna.bsky.social"
        assert sl.detect_platform(f"https://bsky.app/profile/{profile_id}") == "bluesky"
        assert sl.is_valid("bluesky", f"https://bsky.app/profile/{profile_id}") is True
        assert sl.sanitize("bluesky", f"https://bsky.app/profile/{profile_id}") == f"https://bsky.app/profile/{profile_id}"
        # Test direct handle
        assert sl.is_valid("bluesky", profile_id) is True
        assert sl.sanitize("bluesky", profile_id) == f"https://bsky.app/profile/{profile_id}"

    def test_bluesky_with_at(self, sl):
        """Test Bluesky with @ prefix"""
        profile_id = "ysskrishna.bsky.social"
        # Test with @ prefix
        assert sl.is_valid("bluesky", f"@{profile_id}") is True
        assert sl.sanitize("bluesky", f"@{profile_id}") == f"https://bsky.app/profile/{profile_id}"

    def test_bluesky_custom_domain(self, sl):
        """Test Bluesky with custom domain"""
        profile_id = "example.com"
        assert sl.detect_platform(f"https://bsky.app/profile/{profile_id}") == "bluesky"
        assert sl.is_valid("bluesky", f"https://bsky.app/profile/{profile_id}") is True
        assert sl.sanitize("bluesky", f"https://bsky.app/profile/{profile_id}") == f"https://bsky.app/profile/{profile_id}"

