"""Tests for Behance platform."""
import pytest


class TestBehance:
    """Test Behance platform"""

    def test_behance(self, sl):
        """Test Behance platform"""
        profile_id = "ysskrishna"
        assert sl.detect_platform(f"https://behance.net/{profile_id}") == "behance"
        assert sl.is_valid("behance", f"https://behance.net/{profile_id}") is True
        assert sl.sanitize("behance", f"https://behance.net/{profile_id}") == f"https://behance.net/{profile_id}"
        # Test direct username
        assert sl.is_valid("behance", profile_id) is True
        assert sl.sanitize("behance", profile_id) == f"https://behance.net/{profile_id}"

