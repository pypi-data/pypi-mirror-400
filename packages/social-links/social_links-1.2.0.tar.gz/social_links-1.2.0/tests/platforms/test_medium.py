"""Tests for Medium platform."""
import pytest


class TestMedium:
    """Test Medium platform"""

    def test_medium(self, sl):
        """Test Medium platform"""
        profile_id = "ysskrishna"
        assert sl.detect_platform(f"https://medium.com/@{profile_id}") == "medium"
        assert sl.is_valid("medium", f"https://medium.com/@{profile_id}") is True
        assert sl.sanitize("medium", f"https://medium.com/@{profile_id}") == f"https://medium.com/@{profile_id}"
        # Test direct username (with and without @)
        assert sl.is_valid("medium", profile_id) is True
        assert sl.is_valid("medium", f"@{profile_id}") is True
        assert sl.sanitize("medium", profile_id) == f"https://medium.com/@{profile_id}"
        assert sl.sanitize("medium", f"@{profile_id}") == f"https://medium.com/@{profile_id}"

