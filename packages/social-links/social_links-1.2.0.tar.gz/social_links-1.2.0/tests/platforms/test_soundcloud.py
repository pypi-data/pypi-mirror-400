"""Tests for SoundCloud platform."""
import pytest


class TestSoundcloud:
    """Test SoundCloud platform"""

    def test_soundcloud(self, sl):
        """Test SoundCloud platform"""
        profile_id = "ysskrishna"
        assert sl.detect_platform(f"https://soundcloud.com/{profile_id}") == "soundcloud"
        assert sl.is_valid("soundcloud", f"https://soundcloud.com/{profile_id}") is True
        assert sl.sanitize("soundcloud", f"https://soundcloud.com/{profile_id}") == f"https://soundcloud.com/{profile_id}"
        # Test direct username
        assert sl.is_valid("soundcloud", profile_id) is True
        assert sl.sanitize("soundcloud", profile_id) == f"https://soundcloud.com/{profile_id}"

