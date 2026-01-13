"""Tests for Substack platform."""
import pytest


class TestSubstack:
    """Test Substack platform"""

    def test_substack(self, sl):
        """Test Substack platform - all formats sanitize to @username format"""
        profile_id = "ysskrishna"
        
        # Test subdomain format - sanitizes to @username format
        assert sl.detect_platform(f"https://{profile_id}.substack.com") == "substack"
        assert sl.is_valid("substack", f"https://{profile_id}.substack.com") is True
        assert sl.sanitize("substack", f"https://{profile_id}.substack.com") == f"https://substack.com/@{profile_id}"
        
        # Test @username format
        assert sl.detect_platform(f"https://substack.com/@{profile_id}") == "substack"
        assert sl.is_valid("substack", f"https://substack.com/@{profile_id}") is True
        assert sl.sanitize("substack", f"https://substack.com/@{profile_id}") == f"https://substack.com/@{profile_id}"
        
        # Test with www subdomain
        assert sl.is_valid("substack", f"https://www.substack.com/@{profile_id}") is True
        assert sl.sanitize("substack", f"https://www.substack.com/@{profile_id}") == f"https://substack.com/@{profile_id}"
        
        # Test http protocol
        assert sl.is_valid("substack", f"http://substack.com/@{profile_id}") is True
        assert sl.sanitize("substack", f"http://substack.com/@{profile_id}") == f"https://substack.com/@{profile_id}"
        
        # Test with trailing slash
        assert sl.is_valid("substack", f"https://substack.com/@{profile_id}/") is True
        assert sl.sanitize("substack", f"https://substack.com/@{profile_id}/") == f"https://substack.com/@{profile_id}"
        
        # Test direct username - sanitizes to @username format
        assert sl.is_valid("substack", profile_id) is True
        assert sl.sanitize("substack", profile_id) == f"https://substack.com/@{profile_id}"

