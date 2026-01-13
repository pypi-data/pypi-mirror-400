"""Tests for Weibo platform."""
import pytest


class TestWeibo:
    """Test Weibo platform"""

    def test_weibo(self, sl):
        """Test Weibo platform with direct username"""
        username = "guanzhilin"
        assert sl.detect_platform(f"https://weibo.com/{username}") == "weibo"
        assert sl.is_valid("weibo", f"https://weibo.com/{username}") is True
        assert sl.sanitize("weibo", f"https://weibo.com/{username}") == f"https://weibo.com/{username}"
        # Test direct username
        assert sl.is_valid("weibo", username) is True
        assert sl.sanitize("weibo", username) == f"https://weibo.com/{username}"

    def test_weibo_user_id(self, sl):
        """Test Weibo platform with /u/ user ID format"""
        user_id = "1669879400"
        assert sl.detect_platform(f"https://weibo.com/u/{user_id}") == "weibo"
        assert sl.is_valid("weibo", f"https://weibo.com/u/{user_id}") is True
        assert sl.sanitize("weibo", f"https://weibo.com/u/{user_id}") == f"https://weibo.com/u/{user_id}"

    def test_weibo_variations(self, sl):
        """Test Weibo with various URL formats"""
        username = "guanzhilin"
        
        # Test with www subdomain
        assert sl.detect_platform(f"https://www.weibo.com/{username}") == "weibo"
        assert sl.is_valid("weibo", f"https://www.weibo.com/{username}") is True
        assert sl.sanitize("weibo", f"https://www.weibo.com/{username}") == f"https://weibo.com/{username}"
        
        # Test with trailing slash
        assert sl.is_valid("weibo", f"https://weibo.com/{username}/") is True
        assert sl.sanitize("weibo", f"https://weibo.com/{username}/") == f"https://weibo.com/{username}"
        
        # Test http protocol
        assert sl.detect_platform(f"http://weibo.com/{username}") == "weibo"
        assert sl.is_valid("weibo", f"http://weibo.com/{username}") is True
        assert sl.sanitize("weibo", f"http://weibo.com/{username}") == f"https://weibo.com/{username}"
        
        # Test /u/ format with www
        user_id = "1669879400"
        assert sl.is_valid("weibo", f"https://www.weibo.com/u/{user_id}") is True
        assert sl.sanitize("weibo", f"https://www.weibo.com/u/{user_id}") == f"https://weibo.com/u/{user_id}"

