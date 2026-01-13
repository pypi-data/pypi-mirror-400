"""Tests for Telegram platform."""
import pytest


class TestTelegram:
    """Test Telegram platform"""

    def test_telegram(self, sl):
        """Test Telegram platform with t.me"""
        profile_id = "telegram"
        assert sl.detect_platform(f"https://t.me/{profile_id}") == "telegram"
        assert sl.is_valid("telegram", f"https://t.me/{profile_id}") is True
        assert sl.sanitize("telegram", f"https://t.me/{profile_id}") == f"https://t.me/{profile_id}"
        # Test direct username
        assert sl.is_valid("telegram", profile_id) is True
        assert sl.sanitize("telegram", profile_id) == f"https://t.me/{profile_id}"

    def test_telegram_with_underscore(self, sl):
        """Test Telegram with underscores in username"""
        profile_id = "list_telegram"
        assert sl.detect_platform(f"https://t.me/{profile_id}") == "telegram"
        assert sl.is_valid("telegram", f"https://t.me/{profile_id}") is True
        assert sl.sanitize("telegram", f"https://t.me/{profile_id}") == f"https://t.me/{profile_id}"

    def test_telegram_dog(self, sl):
        """Test Telegram dog domain"""
        profile_id = "mrhallo"
        assert sl.detect_platform(f"https://telegram.dog/{profile_id}") == "telegram"
        assert sl.is_valid("telegram", f"https://telegram.dog/{profile_id}") is True
        assert sl.sanitize("telegram", f"https://telegram.dog/{profile_id}") == f"https://t.me/{profile_id}"

    def test_telegram_me(self, sl):
        """Test Telegram.me domain"""
        profile_id = "shajareyan"
        assert sl.detect_platform(f"https://telegram.me/{profile_id}") == "telegram"
        assert sl.is_valid("telegram", f"https://telegram.me/{profile_id}") is True
        assert sl.sanitize("telegram", f"https://telegram.me/{profile_id}") == f"https://t.me/{profile_id}"
        # Test with www
        assert sl.detect_platform(f"https://www.telegram.me/{profile_id}") == "telegram"
        assert sl.is_valid("telegram", f"https://www.telegram.me/{profile_id}") is True
        assert sl.sanitize("telegram", f"https://www.telegram.me/{profile_id}") == f"https://t.me/{profile_id}"

    def test_telegram_web_client_numeric_id(self, sl):
        """Test Telegram web client with numeric ID"""
        # Web client with numeric ID (can be negative for groups/channels)
        numeric_id = "-2128475717"
        web_url = f"https://web.telegram.org/k/#{numeric_id}"
        assert sl.detect_platform(web_url) == "telegram"
        assert sl.is_valid("telegram", web_url) is True
        assert sl.sanitize("telegram", web_url) == f"https://t.me/{numeric_id}"
        
        # Test positive numeric ID
        positive_id = "6891155458"
        web_url_positive = f"http://web.telegram.org/a/#{positive_id}"
        assert sl.detect_platform(web_url_positive) == "telegram"
        assert sl.is_valid("telegram", web_url_positive) is True
        assert sl.sanitize("telegram", web_url_positive) == f"https://t.me/{positive_id}"

    def test_telegram_web_client_username(self, sl):
        """Test Telegram web client with username"""
        username = "Banana_traffbot"
        # Web client can have @ prefix in URL
        web_url = f"https://web.telegram.org/k/#@{username}"
        assert sl.detect_platform(web_url) == "telegram"
        assert sl.is_valid("telegram", web_url) is True
        # @ should be stripped in sanitized output
        assert sl.sanitize("telegram", web_url) == f"https://t.me/{username}"

