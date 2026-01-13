import pytest
import re
from sociallinks.core import SocialLinks
from sociallinks.exceptions import (
    PlatformIDExtractionError,
    URLMismatchError,
)


class TestExtractId:
    """Test _extract_id static method"""

    def test_extract_id_with_named_group(self):
        """Test extracting ID from named group"""
        pattern = re.compile(r"https?://example\.com/(?P<id>[A-Za-z0-9_]+)/?$")
        match = pattern.search("https://example.com/johndoe")
        assert match is not None
        assert SocialLinks._extract_id(match) == "johndoe"

    def test_extract_id_with_unnamed_group(self):
        """Test extracting ID from unnamed group"""
        pattern = re.compile(r"https?://example\.com/([A-Za-z0-9_]+)/?$")
        match = pattern.search("https://example.com/johndoe")
        assert match is not None
        assert SocialLinks._extract_id(match) == "johndoe"

    def test_extract_id_no_match(self):
        """Test extracting ID when no groups match"""
        pattern = re.compile(r"https?://example\.com/")
        match = pattern.search("https://example.com/")
        assert match is not None
        assert SocialLinks._extract_id(match) is None


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_sanitize_no_id_extracted(self):
        """Test sanitize when ID cannot be extracted"""
        sl = SocialLinks(use_predefined_platforms=False)
        # Create a platform with pattern that doesn't capture ID
        platform_data = [{
            "patterns": ["https?://example\\.com/static/?$"],
            "sanitized": "https://example.com/{id}/"
        }]
        sl.set_platform("example", platform_data)
        with pytest.raises(PlatformIDExtractionError, match="Could not extract platform ID"):
            sl.sanitize("example", "https://example.com/static")

    def test_case_insensitive_matching(self):
        """Test case insensitive URL matching"""
        sl = SocialLinks()
        # Should work with uppercase
        assert sl.detect_platform("HTTPS://WWW.LINKEDIN.COM/IN/JOHNDOE/") == "linkedin"
        assert sl.is_valid("linkedin", "HTTPS://WWW.LINKEDIN.COM/IN/JOHNDOE/") is True

    def test_multiple_patterns_same_platform(self):
        """Test platform with multiple patterns"""
        sl = SocialLinks()
        # LinkedIn has both personal and company patterns
        assert sl.is_valid("linkedin", "https://www.linkedin.com/in/johndoe/") is True
        assert sl.is_valid("linkedin", "https://www.linkedin.com/company/acme/") is True


class TestInputTypeValidation:
    """Test input type validation across all public methods"""

    def test_detect_platform_none(self):
        """Test detect_platform with None input"""
        sl = SocialLinks()
        with pytest.raises(TypeError, match="url must be str, not NoneType"):
            sl.detect_platform(None)

    def test_detect_platform_int(self):
        """Test detect_platform with integer input"""
        sl = SocialLinks()
        with pytest.raises(TypeError, match="url must be str, not int"):
            sl.detect_platform(123)

    def test_detect_platform_list(self):
        """Test detect_platform with list input"""
        sl = SocialLinks()
        with pytest.raises(TypeError, match="url must be str, not list"):
            sl.detect_platform(["https://linkedin.com/in/johndoe"])

    def test_detect_platform_dict(self):
        """Test detect_platform with dict input"""
        sl = SocialLinks()
        with pytest.raises(TypeError, match="url must be str, not dict"):
            sl.detect_platform({"url": "https://linkedin.com/in/johndoe"})

    def test_is_valid_none_url(self):
        """Test is_valid with None URL"""
        sl = SocialLinks()
        with pytest.raises(TypeError, match="url must be str, not NoneType"):
            sl.is_valid("linkedin", None)

    def test_is_valid_none_platform(self):
        """Test is_valid with None platform name"""
        sl = SocialLinks()
        with pytest.raises(TypeError, match="platform_name must be str, not NoneType"):
            sl.is_valid(None, "https://linkedin.com/in/johndoe")

    def test_is_valid_int_url(self):
        """Test is_valid with integer URL"""
        sl = SocialLinks()
        with pytest.raises(TypeError, match="url must be str, not int"):
            sl.is_valid("linkedin", 123)

    def test_is_valid_int_platform(self):
        """Test is_valid with integer platform name"""
        sl = SocialLinks()
        with pytest.raises(TypeError, match="platform_name must be str, not int"):
            sl.is_valid(123, "https://linkedin.com/in/johndoe")

    def test_sanitize_none_url(self):
        """Test sanitize with None URL"""
        sl = SocialLinks()
        with pytest.raises(TypeError, match="url must be str, not NoneType"):
            sl.sanitize("linkedin", None)

    def test_sanitize_none_platform(self):
        """Test sanitize with None platform name"""
        sl = SocialLinks()
        with pytest.raises(TypeError, match="platform_name must be str, not NoneType"):
            sl.sanitize(None, "https://linkedin.com/in/johndoe")

    def test_sanitize_int_url(self):
        """Test sanitize with integer URL"""
        sl = SocialLinks()
        with pytest.raises(TypeError, match="url must be str, not int"):
            sl.sanitize("linkedin", 123)

    def test_sanitize_float_url(self):
        """Test sanitize with float URL"""
        sl = SocialLinks()
        with pytest.raises(TypeError, match="url must be str, not float"):
            sl.sanitize("linkedin", 3.14)


class TestEmptyStringHandling:
    """Test empty string and whitespace handling"""

    def test_detect_platform_empty_string(self):
        """Test detect_platform with empty string"""
        sl = SocialLinks()
        assert sl.detect_platform("") is None

    def test_detect_platform_whitespace_only(self):
        """Test detect_platform with whitespace only"""
        sl = SocialLinks()
        assert sl.detect_platform("   ") is None
        assert sl.detect_platform("\t\n") is None
        assert sl.detect_platform("  \t  \n  ") is None

    def test_is_valid_empty_string(self):
        """Test is_valid with empty string URL"""
        sl = SocialLinks()
        assert sl.is_valid("linkedin", "") is False

    def test_is_valid_whitespace_only(self):
        """Test is_valid with whitespace only URL"""
        sl = SocialLinks()
        assert sl.is_valid("linkedin", "   ") is False
        assert sl.is_valid("linkedin", "\t\n") is False

    def test_sanitize_empty_string(self):
        """Test sanitize with empty string URL"""
        sl = SocialLinks()
        with pytest.raises(URLMismatchError, match="URL cannot be empty"):
            sl.sanitize("linkedin", "")

    def test_sanitize_whitespace_only(self):
        """Test sanitize with whitespace only URL"""
        sl = SocialLinks()
        with pytest.raises(URLMismatchError, match="URL cannot be empty"):
            sl.sanitize("linkedin", "   ")
        with pytest.raises(URLMismatchError, match="URL cannot be empty"):
            sl.sanitize("linkedin", "\t\n")

    def test_detect_platform_leading_trailing_whitespace(self):
        """Test that leading/trailing whitespace is properly stripped"""
        sl = SocialLinks()
        url = "  https://www.linkedin.com/in/johndoe/  "
        assert sl.detect_platform(url) == "linkedin"


class TestMalformedURLs:
    """Test handling of malformed and edge case URLs"""

    def test_url_with_special_characters(self):
        """Test URLs with special characters"""
        sl = SocialLinks()
        # Should return None for URLs that don't match any pattern
        assert sl.detect_platform("https://example.com/@#$%^&*()") is None

    def test_url_without_protocol(self):
        """Test URLs without protocol"""
        sl = SocialLinks()
        # Most patterns require protocol, so this should return None
        assert sl.detect_platform("www.linkedin.com/in/johndoe") is None

    def test_very_long_url(self):
        """Test very long URLs (should handle gracefully)"""
        sl = SocialLinks()
        # Create a very long but valid LinkedIn URL
        long_username = "a" * 10000
        long_url = f"https://www.linkedin.com/in/{long_username}/"
        # Should detect platform even with long username
        assert sl.detect_platform(long_url) == "linkedin"

    def test_url_with_unicode_characters(self):
        """Test URLs with Unicode characters - supported by PROFILE_ID_UNICODE pattern"""
        sl = SocialLinks()
        # LinkedIn uses PROFILE_ID_UNICODE which supports Unicode in profile IDs
        unicode_url = "https://www.linkedin.com/in/josé-garcía/"
        assert sl.detect_platform(unicode_url) == "linkedin"
        
        # Should also sanitize correctly
        sanitized = sl.sanitize("linkedin", unicode_url)
        assert sanitized == "https://linkedin.com/in/josé-garcía"

    def test_url_with_query_parameters(self):
        """Test URLs with query parameters - not supported by strict patterns"""
        sl = SocialLinks()
        # Patterns use $ anchor, so query parameters cause mismatch
        url = "https://www.linkedin.com/in/johndoe/?utm_source=test"
        assert sl.detect_platform(url) is None
        
        # Clean URL without query params should work
        clean_url = "https://www.linkedin.com/in/johndoe/"
        assert sl.detect_platform(clean_url) == "linkedin"

    def test_url_with_fragments(self):
        """Test URLs with fragments - not supported by strict patterns"""
        sl = SocialLinks()
        # Patterns use $ anchor, so fragments cause mismatch
        url = "https://www.linkedin.com/in/johndoe/#section"
        assert sl.detect_platform(url) is None
        
        # Clean URL without fragments should work
        clean_url = "https://www.linkedin.com/in/johndoe/"
        assert sl.detect_platform(clean_url) == "linkedin"

    def test_multiple_slashes_in_url(self):
        """Test URLs with multiple consecutive slashes - not supported by strict patterns"""
        sl = SocialLinks()
        # Pattern expects exact format, multiple slashes cause mismatch
        url = "https://www.linkedin.com///in///johndoe///"
        assert sl.detect_platform(url) is None
        
        # Properly formatted URL should work
        clean_url = "https://www.linkedin.com/in/johndoe/"
        assert sl.detect_platform(clean_url) == "linkedin"


class TestEmptyPlatformList:
    """Test behavior with no platforms configured"""

    def test_detect_platform_no_platforms(self):
        """Test detect_platform when no platforms are configured"""
        sl = SocialLinks(use_predefined_platforms=False)
        assert sl.detect_platform("https://www.linkedin.com/in/johndoe/") is None

    def test_is_valid_no_platforms(self):
        """Test is_valid when no platforms are configured"""
        sl = SocialLinks(use_predefined_platforms=False)
        assert sl.is_valid("linkedin", "https://www.linkedin.com/in/johndoe/") is False

