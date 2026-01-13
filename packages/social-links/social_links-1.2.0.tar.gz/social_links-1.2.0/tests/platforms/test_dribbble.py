"""Tests for Dribbble platform."""
import pytest


class TestDribbble:
    """Test Dribbble platform"""

    def test_dribbble(self, sl):
        """Test Dribbble platform"""
        profile_id = "ysskrishna"
        assert sl.detect_platform(f"https://dribbble.com/{profile_id}") == "dribbble"
        assert sl.is_valid("dribbble", f"https://dribbble.com/{profile_id}") is True
        assert sl.sanitize("dribbble", f"https://dribbble.com/{profile_id}") == f"https://dribbble.com/{profile_id}"
        # Test direct username
        assert sl.is_valid("dribbble", profile_id) is True
        assert sl.sanitize("dribbble", profile_id) == f"https://dribbble.com/{profile_id}"

