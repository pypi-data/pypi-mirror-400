"""Tests for Snapchat platform."""
import pytest


class TestSnapchat:
    """Test Snapchat platform"""

    def test_snapchat(self, sl):
        """Test Snapchat platform"""
        profile_id = "ysskrishna"
        assert sl.detect_platform(f"https://snapchat.com/add/{profile_id}") == "snapchat"
        assert sl.is_valid("snapchat", f"https://snapchat.com/add/{profile_id}") is True
        assert sl.sanitize("snapchat", f"https://snapchat.com/add/{profile_id}") == f"https://snapchat.com/@{profile_id}"
        # Test direct username (with and without @)
        assert sl.is_valid("snapchat", profile_id) is True
        assert sl.is_valid("snapchat", f"@{profile_id}") is True
        assert sl.sanitize("snapchat", profile_id) == f"https://snapchat.com/@{profile_id}"
        assert sl.sanitize("snapchat", f"@{profile_id}") == f"https://snapchat.com/@{profile_id}"

    def test_snapchat_at_path(self, sl):
        """Test Snapchat @username path"""
        profile_id = "ysskrishna"
        assert sl.detect_platform(f"https://snapchat.com/@{profile_id}") == "snapchat"
        assert sl.is_valid("snapchat", f"https://snapchat.com/@{profile_id}") is True
        assert sl.sanitize("snapchat", f"https://snapchat.com/@{profile_id}") == f"https://snapchat.com/@{profile_id}"

