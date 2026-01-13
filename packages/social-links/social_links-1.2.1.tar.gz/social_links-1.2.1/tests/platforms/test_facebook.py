"""Tests for Facebook platform."""
import pytest


class TestFacebook:
    """Test Facebook platform"""

    def test_facebook(self, sl):
        """Test Facebook desktop platform"""
        profile_id = "ysskrishna"
        assert sl.detect_platform(f"https://facebook.com/{profile_id}") == "facebook"
        assert sl.is_valid("facebook", f"https://facebook.com/{profile_id}") is True
        assert sl.sanitize("facebook", f"https://facebook.com/{profile_id}") == f"https://facebook.com/{profile_id}"
        # Test direct username
        assert sl.is_valid("facebook", profile_id) is True
        assert sl.sanitize("facebook", profile_id) == f"https://facebook.com/{profile_id}"

    def test_facebook_mobile(self, sl):
        """Test Facebook mobile platform"""
        profile_id = "ysskrishna"
        assert sl.detect_platform(f"https://m.facebook.com/{profile_id}") == "facebook"
        assert sl.is_valid("facebook", f"https://m.facebook.com/{profile_id}") is True
        assert sl.sanitize("facebook", f"https://m.facebook.com/{profile_id}") == f"https://facebook.com/{profile_id}"

