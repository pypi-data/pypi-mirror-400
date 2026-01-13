"""Tests for Stack Overflow platform."""
import pytest


class TestStackoverflow:
    """Test Stack Overflow platform"""

    def test_stackoverflow(self, sl):
        """Test Stack Overflow platform"""
        profile_id = "12345"
        assert sl.detect_platform(f"https://stackoverflow.com/users/{profile_id}") == "stackoverflow"
        assert sl.is_valid("stackoverflow", f"https://stackoverflow.com/users/{profile_id}") is True
        assert sl.sanitize("stackoverflow", f"https://stackoverflow.com/users/{profile_id}") == f"https://stackoverflow.com/users/{profile_id}"
        # Test direct username
        assert sl.is_valid("stackoverflow", profile_id) is True
        assert sl.sanitize("stackoverflow", profile_id) == f"https://stackoverflow.com/users/{profile_id}"

    def test_stackoverflow_full_link(self, sl):
        """Test Stack Overflow with full link including username"""
        profile_id = "3573210"
        full_link = f"https://stackoverflow.com/users/{profile_id}/ysskrishna"
        assert sl.is_valid("stackoverflow", full_link) is True
        assert sl.detect_platform(full_link) == "stackoverflow"
        assert sl.sanitize("stackoverflow", full_link) == f"https://stackoverflow.com/users/{profile_id}"

