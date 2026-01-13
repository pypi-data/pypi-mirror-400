"""Tests for WhatsApp platform."""
import pytest


class TestWhatsapp:
    """Test WhatsApp platform"""

    def test_whatsapp(self, sl):
        """Test WhatsApp platform with wa.me"""
        phone_number = "1234567890"
        assert sl.detect_platform(f"https://wa.me/{phone_number}") == "whatsapp"
        assert sl.is_valid("whatsapp", f"https://wa.me/{phone_number}") is True
        assert sl.sanitize("whatsapp", f"https://wa.me/{phone_number}") == f"https://wa.me/{phone_number}"
        # Test direct phone number
        assert sl.is_valid("whatsapp", phone_number) is True
        assert sl.sanitize("whatsapp", phone_number) == f"https://wa.me/{phone_number}"

    def test_whatsapp_with_plus(self, sl):
        """Test WhatsApp with international format (+)"""
        phone_number = "+1234567890"
        assert sl.detect_platform(f"https://wa.me/{phone_number}") == "whatsapp"
        assert sl.is_valid("whatsapp", f"https://wa.me/{phone_number}") is True
        assert sl.sanitize("whatsapp", f"https://wa.me/{phone_number}") == f"https://wa.me/{phone_number}"
        # Test direct phone number with + (note: + is kept in sanitized output)
        assert sl.is_valid("whatsapp", phone_number) is True
        assert sl.sanitize("whatsapp", phone_number) == f"https://wa.me/{phone_number}"

    def test_whatsapp_send_format(self, sl):
        """Test WhatsApp whatsapp.com/send?phone= format"""
        phone_number = "1234567890"
        # Test whatsapp.com/send?phone= format
        assert sl.detect_platform(f"https://whatsapp.com/send?phone={phone_number}") == "whatsapp"
        assert sl.is_valid("whatsapp", f"https://whatsapp.com/send?phone={phone_number}") is True
        assert sl.sanitize("whatsapp", f"https://whatsapp.com/send?phone={phone_number}") == f"https://wa.me/{phone_number}"
        # Test with www subdomain
        assert sl.is_valid("whatsapp", f"https://www.whatsapp.com/send?phone={phone_number}") is True
        assert sl.sanitize("whatsapp", f"https://www.whatsapp.com/send?phone={phone_number}") == f"https://wa.me/{phone_number}"
        # Test http protocol
        assert sl.is_valid("whatsapp", f"http://whatsapp.com/send?phone={phone_number}") is True
        assert sl.sanitize("whatsapp", f"http://whatsapp.com/send?phone={phone_number}") == f"https://wa.me/{phone_number}"

    def test_whatsapp_send_format_with_plus(self, sl):
        """Test WhatsApp whatsapp.com/send?phone= format with international format"""
        phone_number = "+1234567890"
        # Test whatsapp.com/send?phone= format with +
        assert sl.detect_platform(f"https://whatsapp.com/send?phone={phone_number}") == "whatsapp"
        assert sl.is_valid("whatsapp", f"https://whatsapp.com/send?phone={phone_number}") is True
        assert sl.sanitize("whatsapp", f"https://whatsapp.com/send?phone={phone_number}") == f"https://wa.me/{phone_number}"

