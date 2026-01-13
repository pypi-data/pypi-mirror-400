"""Tests for SlideShare platform."""
import pytest


class TestSlideshare:
    """Test SlideShare platform"""

    def test_slideshare(self, sl):
        """Test SlideShare platform"""
        profile_id = "michaelyublosky"
        assert sl.detect_platform(f"https://www.slideshare.net/{profile_id}") == "slideshare"
        assert sl.is_valid("slideshare", f"https://www.slideshare.net/{profile_id}") is True
        assert sl.sanitize("slideshare", f"https://www.slideshare.net/{profile_id}") == f"https://www.slideshare.net/{profile_id}"
        # Test direct username
        assert sl.is_valid("slideshare", profile_id) is True
        assert sl.sanitize("slideshare", profile_id) == f"https://www.slideshare.net/{profile_id}"

