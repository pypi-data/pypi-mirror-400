"""Tests for Quora platform."""
import pytest


class TestQuora:
    """Test Quora platform"""

    def test_quora_profile(self, sl):
        """Test Quora platform with /profile/ path"""
        username = "Jay-Hoque"
        assert sl.detect_platform(f"https://www.quora.com/profile/{username}") == "quora"
        assert sl.is_valid("quora", f"https://www.quora.com/profile/{username}") is True
        assert sl.sanitize("quora", f"https://www.quora.com/profile/{username}") == f"https://quora.com/profile/{username}"
        # Test direct username
        assert sl.is_valid("quora", username) is True
        assert sl.sanitize("quora", username) == f"https://quora.com/profile/{username}"

    def test_quora_direct_username(self, sl):
        """Test Quora platform with direct username path"""
        username = "Uthma-Faheem"
        assert sl.detect_platform(f"https://www.quora.com/{username}") == "quora"
        assert sl.is_valid("quora", f"https://www.quora.com/{username}") is True
        assert sl.sanitize("quora", f"https://www.quora.com/{username}") == f"https://quora.com/profile/{username}"

    def test_quora_with_unicode(self, sl):
        """Test Quora profile with Unicode characters (URL-encoded)"""
        username = "Nitish-Kumar-%E0%A4%A8%E0%A5%80%E0%A4%A4%E0%A5%80%E0%A4%B6"
        assert sl.detect_platform(f"https://www.quora.com/profile/{username}") == "quora"
        assert sl.is_valid("quora", f"https://www.quora.com/profile/{username}") is True
        assert sl.sanitize("quora", f"https://www.quora.com/profile/{username}") == f"https://quora.com/profile/{username}"

