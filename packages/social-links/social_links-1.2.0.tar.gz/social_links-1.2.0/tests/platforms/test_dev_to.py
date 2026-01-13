"""Tests for Dev.to platform."""
import pytest


class TestDevTo:
    """Test Dev.to platform"""

    def test_dev_to(self, sl):
        """Test Dev.to platform"""
        profile_id = "ysskrishna"
        assert sl.detect_platform(f"https://dev.to/{profile_id}") == "dev_to"
        assert sl.is_valid("dev_to", f"https://dev.to/{profile_id}") is True
        assert sl.sanitize("dev_to", f"https://dev.to/{profile_id}") == f"https://dev.to/{profile_id}"
        # Test direct username
        assert sl.is_valid("dev_to", profile_id) is True
        assert sl.sanitize("dev_to", profile_id) == f"https://dev.to/{profile_id}"

