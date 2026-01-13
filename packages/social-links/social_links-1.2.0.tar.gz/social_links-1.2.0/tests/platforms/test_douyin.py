"""Tests for Douyin platform."""
import pytest


class TestDouyin:
    """Test Douyin platform"""

    def test_douyin(self, sl):
        """Test Douyin platform"""
        user_id = "MS4wLjABAAAA9yeV8IIJxpee3_u9zb_Al3_mOA8IffgD3_ueMCQUly4"
        assert sl.detect_platform(f"https://www.douyin.com/user/{user_id}") == "douyin"
        assert sl.is_valid("douyin", f"https://www.douyin.com/user/{user_id}") is True
        assert sl.sanitize("douyin", f"https://www.douyin.com/user/{user_id}") == f"https://www.douyin.com/user/{user_id}"
        # Test direct user ID
        assert sl.is_valid("douyin", user_id) is True
        assert sl.sanitize("douyin", user_id) == f"https://www.douyin.com/user/{user_id}"

    def test_douyin_variations(self, sl):
        """Test Douyin with various URL formats"""
        user_id = "MS4wLjABAAAA9yeV8IIJxpee3_u9zb_Al3_mOA8IffgD3_ueMCQUly4"
        
        # Test without www subdomain
        assert sl.detect_platform(f"https://douyin.com/user/{user_id}") == "douyin"
        assert sl.is_valid("douyin", f"https://douyin.com/user/{user_id}") is True
        assert sl.sanitize("douyin", f"https://douyin.com/user/{user_id}") == f"https://www.douyin.com/user/{user_id}"
        
        # Test with trailing slash
        assert sl.is_valid("douyin", f"https://www.douyin.com/user/{user_id}/") is True
        assert sl.sanitize("douyin", f"https://www.douyin.com/user/{user_id}/") == f"https://www.douyin.com/user/{user_id}"
        
        # Test http protocol
        assert sl.detect_platform(f"http://www.douyin.com/user/{user_id}") == "douyin"
        assert sl.is_valid("douyin", f"http://www.douyin.com/user/{user_id}") is True
        assert sl.sanitize("douyin", f"http://www.douyin.com/user/{user_id}") == f"https://www.douyin.com/user/{user_id}"

