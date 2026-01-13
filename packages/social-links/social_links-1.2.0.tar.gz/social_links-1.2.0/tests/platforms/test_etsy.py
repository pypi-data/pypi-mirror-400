"""Tests for Etsy platform."""
import pytest


class TestEtsy:
    """Test Etsy platform"""

    def test_etsy(self, sl):
        """Test Etsy platform"""
        shop_name = "MyShopName"
        assert sl.detect_platform(f"https://etsy.com/shop/{shop_name}") == "etsy"
        assert sl.is_valid("etsy", f"https://etsy.com/shop/{shop_name}") is True
        assert sl.sanitize("etsy", f"https://etsy.com/shop/{shop_name}") == f"https://etsy.com/shop/{shop_name}"
        # Test direct shop name
        assert sl.is_valid("etsy", shop_name) is True
        assert sl.sanitize("etsy", shop_name) == f"https://etsy.com/shop/{shop_name}"

