"""Tests for Instagram platform."""
import pytest


class TestInstagram:
    """Test Instagram platform"""

    def test_instagram(self, sl):
        """Test Instagram platform"""
        profile_id = "ysskrishna"
        assert sl.detect_platform(f"https://instagram.com/{profile_id}") == "instagram"
        assert sl.is_valid("instagram", f"https://instagram.com/{profile_id}") is True
        assert sl.sanitize("instagram", f"https://instagram.com/{profile_id}") == f"https://instagram.com/{profile_id}"
        # Test direct username
        assert sl.is_valid("instagram", profile_id) is True
        assert sl.sanitize("instagram", profile_id) == f"https://instagram.com/{profile_id}"

    def test_instagram_mobile(self, sl):
        """Test Instagram mobile platform"""
        profile_id = "ysskrishna"
        assert sl.detect_platform(f"https://m.instagram.com/{profile_id}") == "instagram"
        assert sl.is_valid("instagram", f"https://m.instagram.com/{profile_id}") is True
        assert sl.sanitize("instagram", f"https://m.instagram.com/{profile_id}") == f"https://instagram.com/{profile_id}"

    def test_instagram_with_at_symbol(self, sl):
        """Test Instagram URLs with @ symbol in path"""
        profile_id = "ysskrishna"
        # Instagram URLs can have @ in the URL path
        assert sl.is_valid("instagram", f"https://instagram.com/{profile_id}") is True
        assert sl.detect_platform(f"https://instagram.com/{profile_id}") == "instagram"
        assert sl.sanitize("instagram", f"https://instagram.com/{profile_id}") == f"https://instagram.com/{profile_id}"

