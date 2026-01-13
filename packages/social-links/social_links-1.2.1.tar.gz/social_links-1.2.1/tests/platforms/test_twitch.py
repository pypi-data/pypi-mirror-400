"""Tests for Twitch platform."""
import pytest


class TestTwitch:
    """Test Twitch platform"""

    def test_twitch(self, sl):
        """Test Twitch platform"""
        profile_id = "ysskrishna"
        assert sl.detect_platform(f"https://twitch.tv/{profile_id}") == "twitch"
        assert sl.is_valid("twitch", f"https://twitch.tv/{profile_id}") is True
        assert sl.sanitize("twitch", f"https://twitch.tv/{profile_id}") == f"https://twitch.tv/{profile_id}"
        # Test direct username
        assert sl.is_valid("twitch", profile_id) is True
        assert sl.sanitize("twitch", profile_id) == f"https://twitch.tv/{profile_id}"

    def test_twitch_mobile(self, sl):
        """Test Twitch mobile platform"""
        profile_id = "ysskrishna"
        assert sl.detect_platform(f"https://m.twitch.tv/{profile_id}") == "twitch"
        assert sl.is_valid("twitch", f"https://m.twitch.tv/{profile_id}") is True
        assert sl.sanitize("twitch", f"https://m.twitch.tv/{profile_id}") == f"https://twitch.tv/{profile_id}"

