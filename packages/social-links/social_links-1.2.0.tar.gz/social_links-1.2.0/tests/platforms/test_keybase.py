"""Tests for Keybase platform."""
import pytest


class TestKeybase:
    """Test Keybase platform"""

    def test_keybase(self, sl):
        """Test Keybase platform"""
        profile_id = "ysskrishna"
        assert sl.detect_platform(f"https://keybase.io/{profile_id}") == "keybase"
        assert sl.is_valid("keybase", f"https://keybase.io/{profile_id}") is True
        assert sl.sanitize("keybase", f"https://keybase.io/{profile_id}") == f"https://keybase.io/{profile_id}"
        # Test direct username
        assert sl.is_valid("keybase", profile_id) is True
        assert sl.sanitize("keybase", profile_id) == f"https://keybase.io/{profile_id}"

