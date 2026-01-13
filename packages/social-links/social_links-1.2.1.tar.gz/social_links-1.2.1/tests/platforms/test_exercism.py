"""Tests for Exercism platform."""
import pytest


class TestExercism:
    """Test Exercism platform"""

    def test_exercism(self, sl):
        """Test Exercism platform"""
        profile_id = "ysskrishna"
        assert sl.detect_platform(f"https://exercism.io/profiles/{profile_id}") == "exercism"
        assert sl.is_valid("exercism", f"https://exercism.io/profiles/{profile_id}") is True
        assert sl.sanitize("exercism", f"https://exercism.io/profiles/{profile_id}") == f"https://exercism.io/profiles/{profile_id}"
        # Test direct username
        assert sl.is_valid("exercism", profile_id) is True
        assert sl.sanitize("exercism", profile_id) == f"https://exercism.io/profiles/{profile_id}"

