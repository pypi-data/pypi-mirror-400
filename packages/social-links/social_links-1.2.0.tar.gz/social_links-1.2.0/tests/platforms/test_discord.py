"""Tests for Discord platform."""
import pytest


class TestDiscord:
    """Test Discord platform"""

    def test_discord(self, sl):
        """Test Discord platform with discord.gg"""
        invite_code = "ysskrishna"
        assert sl.detect_platform(f"https://discord.gg/{invite_code}") == "discord"
        assert sl.is_valid("discord", f"https://discord.gg/{invite_code}") is True
        assert sl.sanitize("discord", f"https://discord.gg/{invite_code}") == f"https://discord.gg/{invite_code}"
        # Test direct invite code
        assert sl.is_valid("discord", invite_code) is True
        assert sl.sanitize("discord", invite_code) == f"https://discord.gg/{invite_code}"

    def test_discord_invite_url(self, sl):
        """Test Discord platform with discord.com/invite"""
        invite_code = "ysskrishna"
        # Test discord.com/invite format - should normalize to discord.gg
        assert sl.detect_platform(f"https://discord.com/invite/{invite_code}") == "discord"
        assert sl.is_valid("discord", f"https://discord.com/invite/{invite_code}") is True
        assert sl.sanitize("discord", f"https://discord.com/invite/{invite_code}") == f"https://discord.gg/{invite_code}"

