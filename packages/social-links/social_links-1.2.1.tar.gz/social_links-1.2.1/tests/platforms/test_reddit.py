"""Tests for Reddit platform."""
import pytest


class TestReddit:
    """Test Reddit platform"""

    def test_reddit(self, sl):
        """Test Reddit platform"""
        profile_id = "ysskrishna"
        assert sl.detect_platform(f"https://reddit.com/user/{profile_id}") == "reddit"
        assert sl.is_valid("reddit", f"https://reddit.com/user/{profile_id}") is True
        assert sl.sanitize("reddit", f"https://reddit.com/user/{profile_id}") == f"https://reddit.com/user/{profile_id}"
        # Test direct username
        assert sl.is_valid("reddit", profile_id) is True
        assert sl.sanitize("reddit", profile_id) == f"https://reddit.com/user/{profile_id}"

    def test_reddit_u_path(self, sl):
        """Test Reddit /u/ path"""
        profile_id = "ysskrishna"
        assert sl.detect_platform(f"https://reddit.com/u/{profile_id}") == "reddit"
        assert sl.is_valid("reddit", f"https://reddit.com/u/{profile_id}") is True
        assert sl.sanitize("reddit", f"https://reddit.com/u/{profile_id}") == f"https://reddit.com/user/{profile_id}"

    def test_reddit_old(self, sl):
        """Test Reddit old.reddit.com"""
        profile_id = "ysskrishna"
        assert sl.detect_platform(f"https://old.reddit.com/user/{profile_id}") == "reddit"
        assert sl.is_valid("reddit", f"https://old.reddit.com/user/{profile_id}") is True
        assert sl.sanitize("reddit", f"https://old.reddit.com/user/{profile_id}") == f"https://reddit.com/user/{profile_id}"
        # Test old.reddit.com with /u/ path
        assert sl.detect_platform(f"https://old.reddit.com/u/{profile_id}") == "reddit"
        assert sl.is_valid("reddit", f"https://old.reddit.com/u/{profile_id}") is True
        assert sl.sanitize("reddit", f"https://old.reddit.com/u/{profile_id}") == f"https://reddit.com/user/{profile_id}"

    def test_reddit_u_prefix(self, sl):
        """Test Reddit u/ prefix format (e.g., u/username)"""
        profile_id = "ysskrishna"
        # Test u/username format
        assert sl.detect_platform(f"u/{profile_id}") == "reddit"
        assert sl.is_valid("reddit", f"u/{profile_id}") is True
        assert sl.sanitize("reddit", f"u/{profile_id}") == f"https://reddit.com/user/{profile_id}"

    def test_reddit_subreddit(self, sl):
        """Test Reddit subreddit /r/ path"""
        subreddit_name = "python"
        assert sl.detect_platform(f"https://reddit.com/r/{subreddit_name}") == "reddit"
        assert sl.is_valid("reddit", f"https://reddit.com/r/{subreddit_name}") is True
        assert sl.sanitize("reddit", f"https://reddit.com/r/{subreddit_name}") == f"https://reddit.com/r/{subreddit_name}"

    def test_reddit_subreddit_variations(self, sl):
        """Test Reddit subreddit with various URL formats"""
        subreddit_name = "learnprogramming"
        
        # Test www subdomain
        assert sl.detect_platform(f"https://www.reddit.com/r/{subreddit_name}") == "reddit"
        assert sl.is_valid("reddit", f"https://www.reddit.com/r/{subreddit_name}") is True
        assert sl.sanitize("reddit", f"https://www.reddit.com/r/{subreddit_name}") == f"https://reddit.com/r/{subreddit_name}"
        
        # Test old.reddit.com
        assert sl.detect_platform(f"https://old.reddit.com/r/{subreddit_name}") == "reddit"
        assert sl.is_valid("reddit", f"https://old.reddit.com/r/{subreddit_name}") is True
        assert sl.sanitize("reddit", f"https://old.reddit.com/r/{subreddit_name}") == f"https://reddit.com/r/{subreddit_name}"
        
        # Test with trailing slash
        assert sl.is_valid("reddit", f"https://reddit.com/r/{subreddit_name}/") is True
        assert sl.sanitize("reddit", f"https://reddit.com/r/{subreddit_name}/") == f"https://reddit.com/r/{subreddit_name}"
        
        # Test http protocol
        assert sl.detect_platform(f"http://reddit.com/r/{subreddit_name}") == "reddit"
        assert sl.is_valid("reddit", f"http://reddit.com/r/{subreddit_name}") is True
        assert sl.sanitize("reddit", f"http://reddit.com/r/{subreddit_name}") == f"https://reddit.com/r/{subreddit_name}"

    def test_reddit_subreddit_r_prefix(self, sl):
        """Test Reddit r/ prefix format (e.g., r/subreddit)"""
        subreddit_name = "python"
        # Test r/subreddit format
        assert sl.detect_platform(f"r/{subreddit_name}") == "reddit"
        assert sl.is_valid("reddit", f"r/{subreddit_name}") is True
        assert sl.sanitize("reddit", f"r/{subreddit_name}") == f"https://reddit.com/r/{subreddit_name}"

