"""Tests for Bandcamp platform."""
import pytest


class TestBandcamp:
    """Test Bandcamp platform"""

    def test_bandcamp(self, sl):
        """Test Bandcamp platform with subdomain"""
        profile_id = "ysskrishna"
        assert sl.detect_platform(f"https://{profile_id}.bandcamp.com") == "bandcamp"
        assert sl.is_valid("bandcamp", f"https://{profile_id}.bandcamp.com") is True
        assert sl.sanitize("bandcamp", f"https://{profile_id}.bandcamp.com") == f"https://{profile_id}.bandcamp.com"
        # Test direct username
        assert sl.is_valid("bandcamp", profile_id) is True
        assert sl.sanitize("bandcamp", profile_id) == f"https://{profile_id}.bandcamp.com"

    def test_bandcamp_with_dashes(self, sl):
        """Test Bandcamp with dashes in username"""
        profile_id = "my-band-name"
        assert sl.detect_platform(f"https://{profile_id}.bandcamp.com") == "bandcamp"
        assert sl.is_valid("bandcamp", f"https://{profile_id}.bandcamp.com") is True
        assert sl.sanitize("bandcamp", f"https://{profile_id}.bandcamp.com") == f"https://{profile_id}.bandcamp.com"

