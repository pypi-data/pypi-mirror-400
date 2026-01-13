"""Tests for Patreon platform."""
import pytest


class TestPatreon:
    """Test Patreon platform"""

    def test_patreon(self, sl):
        """Test Patreon platform"""
        profile_id = "ysskrishna"
        assert sl.detect_platform(f"https://patreon.com/{profile_id}") == "patreon"
        assert sl.is_valid("patreon", f"https://patreon.com/{profile_id}") is True
        assert sl.sanitize("patreon", f"https://patreon.com/{profile_id}") == f"https://patreon.com/{profile_id}"
        # Test direct username
        assert sl.is_valid("patreon", profile_id) is True
        assert sl.sanitize("patreon", profile_id) == f"https://patreon.com/{profile_id}"

