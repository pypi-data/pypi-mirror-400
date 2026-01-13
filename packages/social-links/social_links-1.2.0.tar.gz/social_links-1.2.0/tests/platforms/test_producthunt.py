"""Tests for ProductHunt platform."""
import pytest


class TestProducthunt:
    """Test ProductHunt platform"""

    def test_producthunt(self, sl):
        """Test ProductHunt platform"""
        profile_id = "ysskrishna"
        assert sl.detect_platform(f"https://www.producthunt.com/@{profile_id}") == "producthunt"
        assert sl.is_valid("producthunt", f"https://www.producthunt.com/@{profile_id}") is True
        assert sl.sanitize("producthunt", f"https://www.producthunt.com/@{profile_id}") == f"https://www.producthunt.com/@{profile_id}"
        # Test direct username (with and without @)
        assert sl.is_valid("producthunt", profile_id) is True
        assert sl.is_valid("producthunt", f"@{profile_id}") is True
        assert sl.sanitize("producthunt", profile_id) == f"https://www.producthunt.com/@{profile_id}"
        assert sl.sanitize("producthunt", f"@{profile_id}") == f"https://www.producthunt.com/@{profile_id}"

