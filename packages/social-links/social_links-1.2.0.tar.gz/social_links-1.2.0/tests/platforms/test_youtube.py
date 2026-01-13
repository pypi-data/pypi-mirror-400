"""Tests for YouTube platform."""
import pytest


class TestYoutube:
    """Test YouTube platform"""

    def test_youtube(self, sl):
        """Test YouTube platform"""
        profile_id = "@ysskrishna"
        assert sl.detect_platform(f"https://youtube.com/{profile_id}") == "youtube"
        assert sl.is_valid("youtube", f"https://youtube.com/{profile_id}") is True
        assert sl.sanitize("youtube", f"https://youtube.com/{profile_id}") == f"https://youtube.com/{profile_id}"

    def test_youtube_channel(self, sl):
        """Test YouTube channel URL"""
        profile_id = "UC1234567890"
        assert sl.detect_platform(f"https://youtube.com/channel/{profile_id}") == "youtube"
        assert sl.is_valid("youtube", f"https://youtube.com/channel/{profile_id}") is True
        assert sl.sanitize("youtube", f"https://youtube.com/channel/{profile_id}") == f"https://youtube.com/{profile_id}"

    def test_youtube_user(self, sl):
        """Test YouTube user URL"""
        profile_id = "ysskrishna"
        assert sl.detect_platform(f"https://youtube.com/user/{profile_id}") == "youtube"
        assert sl.is_valid("youtube", f"https://youtube.com/user/{profile_id}") is True
        assert sl.sanitize("youtube", f"https://youtube.com/user/{profile_id}") == f"https://youtube.com/{profile_id}"

    def test_youtube_mobile(self, sl):
        """Test YouTube mobile URL"""
        profile_id = "ysskrishna"
        assert sl.detect_platform(f"https://m.youtube.com/c/{profile_id}") == "youtube"
        assert sl.is_valid("youtube", f"https://m.youtube.com/c/{profile_id}") is True
        assert sl.sanitize("youtube", f"https://m.youtube.com/c/{profile_id}") == f"https://youtube.com/{profile_id}"

    def test_youtube_various_formats(self, sl):
        """Test YouTube with various URL formats (matching PHP test cases)"""
        profile_id = "Google"
        # Test www.youtube.com/user/Google
        assert sl.detect_platform(f"https://www.youtube.com/user/{profile_id}") == "youtube"
        assert sl.is_valid("youtube", f"https://www.youtube.com/user/{profile_id}") is True
        assert sl.sanitize("youtube", f"https://www.youtube.com/user/{profile_id}") == f"https://youtube.com/{profile_id}"
        # Test www.youtube.com/c/Google
        assert sl.detect_platform(f"https://www.youtube.com/c/{profile_id}") == "youtube"
        assert sl.is_valid("youtube", f"https://www.youtube.com/c/{profile_id}") is True
        assert sl.sanitize("youtube", f"https://www.youtube.com/c/{profile_id}") == f"https://youtube.com/{profile_id}"
        # Test www.youtube.com/Google
        assert sl.detect_platform(f"https://www.youtube.com/{profile_id}") == "youtube"
        assert sl.is_valid("youtube", f"https://www.youtube.com/{profile_id}") is True
        assert sl.sanitize("youtube", f"https://www.youtube.com/{profile_id}") == f"https://youtube.com/{profile_id}"
        # Test www.youtube.com/Google/ (with trailing slash)
        assert sl.detect_platform(f"https://www.youtube.com/{profile_id}/") == "youtube"
        assert sl.is_valid("youtube", f"https://www.youtube.com/{profile_id}/") is True
        assert sl.sanitize("youtube", f"https://www.youtube.com/{profile_id}/") == f"https://youtube.com/{profile_id}"
        # Test youtube.com/Google (without www)
        assert sl.detect_platform(f"https://youtube.com/{profile_id}") == "youtube"
        assert sl.is_valid("youtube", f"https://youtube.com/{profile_id}") is True
        assert sl.sanitize("youtube", f"https://youtube.com/{profile_id}") == f"https://youtube.com/{profile_id}"
        # Test http://www.youtube.com/Google (http instead of https)
        assert sl.detect_platform(f"http://www.youtube.com/{profile_id}") == "youtube"
        assert sl.is_valid("youtube", f"http://www.youtube.com/{profile_id}") is True
        assert sl.sanitize("youtube", f"http://www.youtube.com/{profile_id}") == f"https://youtube.com/{profile_id}"

