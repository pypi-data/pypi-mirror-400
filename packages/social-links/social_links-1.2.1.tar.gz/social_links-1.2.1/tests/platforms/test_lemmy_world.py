"""Tests for Lemmy World platform."""
import pytest


class TestLemmyWorld:
    """Test Lemmy World platform"""

    def test_lemmy_world(self, sl):
        """Test Lemmy World platform"""
        profile_id = "ysskrishna"
        assert sl.detect_platform(f"https://lemmy.world/u/{profile_id}") == "lemmy_world"
        assert sl.is_valid("lemmy_world", f"https://lemmy.world/u/{profile_id}") is True
        assert sl.sanitize("lemmy_world", f"https://lemmy.world/u/{profile_id}") == f"https://lemmy.world/u/{profile_id}"
        # Test direct username
        assert sl.is_valid("lemmy_world", profile_id) is True
        assert sl.sanitize("lemmy_world", profile_id) == f"https://lemmy.world/u/{profile_id}"

