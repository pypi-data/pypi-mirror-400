"""Tests for TikTok platform."""
import pytest


class TestTiktok:
    """Test TikTok platform"""

    def test_tiktok(self, sl):
        """Test TikTok platform"""
        profile_id = "ysskrishna"
        assert sl.detect_platform(f"https://tiktok.com/@{profile_id}") == "tiktok"
        assert sl.is_valid("tiktok", f"https://tiktok.com/@{profile_id}") is True
        assert sl.sanitize("tiktok", f"https://tiktok.com/@{profile_id}") == f"https://tiktok.com/@{profile_id}"
        # Test direct username (with and without @)
        assert sl.is_valid("tiktok", profile_id) is True
        assert sl.is_valid("tiktok", f"@{profile_id}") is True
        assert sl.sanitize("tiktok", profile_id) == f"https://tiktok.com/@{profile_id}"
        assert sl.sanitize("tiktok", f"@{profile_id}") == f"https://tiktok.com/@{profile_id}"
        # Test www and http variations
        assert sl.is_valid("tiktok", f"https://www.tiktok.com/@{profile_id}") is True
        assert sl.sanitize("tiktok", f"https://www.tiktok.com/@{profile_id}") == f"https://tiktok.com/@{profile_id}"
        assert sl.is_valid("tiktok", f"http://www.tiktok.com/@{profile_id}") is True
        assert sl.sanitize("tiktok", f"http://www.tiktok.com/@{profile_id}") == f"https://tiktok.com/@{profile_id}"

