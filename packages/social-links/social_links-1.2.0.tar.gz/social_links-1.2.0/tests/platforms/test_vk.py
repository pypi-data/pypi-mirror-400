"""Tests for VK platform."""
import pytest


class TestVk:
    """Test VK platform"""

    def test_vk(self, sl):
        """Test VK platform"""
        profile_id = "ysskrishna"
        assert sl.detect_platform(f"https://vk.com/{profile_id}") == "vk"
        assert sl.is_valid("vk", f"https://vk.com/{profile_id}") is True
        assert sl.sanitize("vk", f"https://vk.com/{profile_id}") == f"https://vk.com/{profile_id}"
        # Test direct username (with and without @)
        assert sl.is_valid("vk", profile_id) is True
        assert sl.is_valid("vk", f"@{profile_id}") is True
        assert sl.sanitize("vk", profile_id) == f"https://vk.com/{profile_id}"
        assert sl.sanitize("vk", f"@{profile_id}") == f"https://vk.com/{profile_id}"

    def test_vk_mobile(self, sl):
        """Test VK mobile platform"""
        profile_id = "ysskrishna"
        assert sl.detect_platform(f"https://m.vk.com/{profile_id}") == "vk"
        assert sl.is_valid("vk", f"https://m.vk.com/{profile_id}") is True
        assert sl.sanitize("vk", f"https://m.vk.com/{profile_id}") == f"https://vk.com/{profile_id}"

