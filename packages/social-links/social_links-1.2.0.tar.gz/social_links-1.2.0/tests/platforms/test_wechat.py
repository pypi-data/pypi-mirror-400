"""Tests for WeChat platform."""
import pytest


class TestWechat:
    """Test WeChat platform"""

    def test_wechat(self, sl):
        """Test WeChat platform with open.weixin.qq.com format"""
        username = "DutchEmbassy_BJ"
        assert sl.detect_platform(f"https://open.weixin.qq.com/qr/code?username={username}") == "wechat"
        assert sl.is_valid("wechat", f"https://open.weixin.qq.com/qr/code?username={username}") is True
        assert sl.sanitize("wechat", f"https://open.weixin.qq.com/qr/code?username={username}") == f"https://open.weixin.qq.com/qr/code?username={username}"
        # Test direct username
        assert sl.is_valid("wechat", username) is True
        assert sl.sanitize("wechat", username) == f"https://open.weixin.qq.com/qr/code?username={username}"

    def test_wechat_weixin_protocol(self, sl):
        """Test WeChat with weixin:// protocol"""
        username = "Bright_Writers"
        assert sl.detect_platform(f"weixin://dl/chat?{username}") == "wechat"
        assert sl.is_valid("wechat", f"weixin://dl/chat?{username}") is True
        assert sl.sanitize("wechat", f"weixin://dl/chat?{username}") == f"https://open.weixin.qq.com/qr/code?username={username}"

