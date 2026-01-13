"""Tests for Linktree platform."""
import pytest


class TestLinktree:
    """Test Linktree platform"""

    def test_linktree(self, sl):
        """Test Linktree platform"""
        profile_id = "ysskrishna"
        assert sl.detect_platform(f"https://linktr.ee/{profile_id}") == "linktree"
        assert sl.is_valid("linktree", f"https://linktr.ee/{profile_id}") is True
        assert sl.sanitize("linktree", f"https://linktr.ee/{profile_id}") == f"https://linktr.ee/{profile_id}"
        # Test direct username
        assert sl.is_valid("linktree", profile_id) is True
        assert sl.sanitize("linktree", profile_id) == f"https://linktr.ee/{profile_id}"

