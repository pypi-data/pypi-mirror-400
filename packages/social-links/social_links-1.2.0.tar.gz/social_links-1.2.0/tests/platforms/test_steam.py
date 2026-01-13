"""Tests for Steam platform."""
import pytest


class TestSteam:
    """Test Steam platform"""

    def test_steam_id(self, sl):
        """Test Steam platform with /id/ path"""
        username = "pepepro76561198317693716"
        assert sl.detect_platform(f"https://steamcommunity.com/id/{username}") == "steam"
        assert sl.is_valid("steam", f"https://steamcommunity.com/id/{username}") is True
        assert sl.sanitize("steam", f"https://steamcommunity.com/id/{username}") == f"https://steamcommunity.com/id/{username}"
        # Test direct username
        assert sl.is_valid("steam", username) is True
        assert sl.sanitize("steam", username) == f"https://steamcommunity.com/id/{username}"

    def test_steam_profiles(self, sl):
        """Test Steam platform with /profiles/ path (numeric Steam ID)"""
        steam_id = "76561198014898339"
        assert sl.detect_platform(f"https://steamcommunity.com/profiles/{steam_id}") == "steam"
        assert sl.is_valid("steam", f"https://steamcommunity.com/profiles/{steam_id}") is True
        # Profiles path should be preserved (not converted to /id/)
        assert sl.sanitize("steam", f"https://steamcommunity.com/profiles/{steam_id}") == f"https://steamcommunity.com/profiles/{steam_id}"

