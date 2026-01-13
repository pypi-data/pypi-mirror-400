"""Tests for Vimeo platform."""
import pytest


class TestVimeo:
    """Test Vimeo platform"""

    def test_vimeo(self, sl):
        """Test Vimeo platform"""
        profile_id = "ysskrishna"
        assert sl.detect_platform(f"https://vimeo.com/{profile_id}") == "vimeo"
        assert sl.is_valid("vimeo", f"https://vimeo.com/{profile_id}") is True
        assert sl.sanitize("vimeo", f"https://vimeo.com/{profile_id}") == f"https://vimeo.com/{profile_id}"
        # Test direct username
        assert sl.is_valid("vimeo", profile_id) is True
        assert sl.sanitize("vimeo", profile_id) == f"https://vimeo.com/{profile_id}"

