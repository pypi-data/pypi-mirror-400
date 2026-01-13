"""Tests for LinkedIn platform."""
import pytest


class TestLinkedin:
    """Test LinkedIn platform"""

    def test_linkedin_personal(self, sl):
        """Test LinkedIn personal profile"""
        profile_id = "ysskrishna"
        assert sl.detect_platform(f"https://linkedin.com/in/{profile_id}") == "linkedin"
        assert sl.is_valid("linkedin", f"https://linkedin.com/in/{profile_id}") is True
        assert sl.sanitize("linkedin", f"https://linkedin.com/in/{profile_id}") == f"https://linkedin.com/in/{profile_id}"
        # Test direct username
        assert sl.is_valid("linkedin", profile_id) is True
        assert sl.sanitize("linkedin", profile_id) == f"https://linkedin.com/in/{profile_id}"

    def test_linkedin_company(self, sl):
        """Test LinkedIn company profile"""
        profile_id = "acme"
        assert sl.detect_platform(f"https://linkedin.com/company/{profile_id}") == "linkedin"
        assert sl.is_valid("linkedin", f"https://linkedin.com/company/{profile_id}") is True
        assert sl.sanitize("linkedin", f"https://linkedin.com/company/{profile_id}") == f"https://linkedin.com/company/{profile_id}"

    def test_linkedin_mobile(self, sl):
        """Test LinkedIn mobile platform"""
        profile_id = "ysskrishna"
        assert sl.detect_platform(f"https://linkedin.com/mwlite/in/{profile_id}") == "linkedin"
        assert sl.is_valid("linkedin", f"https://linkedin.com/mwlite/in/{profile_id}") is True
        assert sl.sanitize("linkedin", f"https://linkedin.com/mwlite/in/{profile_id}") == f"https://linkedin.com/in/{profile_id}"

    def test_linkedin_localized(self, sl):
        """Test LinkedIn localized URLs (e.g., de.linkedin.com)"""
        profile_id = "ysskrishna"
        # Test localized personal profile
        assert sl.is_valid("linkedin", f"https://de.linkedin.com/in/{profile_id}/") is True
        assert sl.sanitize("linkedin", f"https://de.linkedin.com/in/{profile_id}/") == f"https://linkedin.com/in/{profile_id}"
        # Test localized mobile profile
        assert sl.is_valid("linkedin", f"https://de.linkedin.com/mwlite/in/{profile_id}/") is True
        assert sl.sanitize("linkedin", f"https://de.linkedin.com/mwlite/in/{profile_id}/") == f"https://linkedin.com/in/{profile_id}"

    def test_linkedin_additional_test_cases(self, sl):
        """Test LinkedIn additional test cases from PHP NormalizersTest.php"""
        
        # LinkedIn profile test cases (from testLinkedinProfileNormalizer)
        profile_test_cases = [
            ('https://www.linkedin.com/in/dealroom/', 'https://linkedin.com/in/dealroom'),
            ('https://www.linkedin.com/in/dealroom', 'https://linkedin.com/in/dealroom'),
            ('http://www.linkedin.com/in/dealroom/', 'https://linkedin.com/in/dealroom'),
            ('http://de.linkedin.com/in/dealroom/', 'https://linkedin.com/in/dealroom'),
            ('https://de.linkedin.com/in/peter-müller-81a8/', 'https://linkedin.com/in/peter-müller-81a8'),
        ]
        
        for source, expected in profile_test_cases:
            assert sl.is_valid("linkedin", source) is True, f"URL should be valid: {source}"
            result = sl.sanitize("linkedin", source)
            assert result == expected, f"Expected {expected}, got {result} for {source}"
        
        # LinkedIn company test cases 
        company_test_cases = [
            ('https://www.linkedin.com/company/dealroom/', 'https://linkedin.com/company/dealroom'),
            ('https://www.linkedin.com/company/dealroom', 'https://linkedin.com/company/dealroom'),
            ('http://www.linkedin.com/company/dealroom/', 'https://linkedin.com/company/dealroom'),
            ('https://linkedin.com/company/dealroom/', 'https://linkedin.com/company/dealroom'),
            ('https://www.linkedin.com/company/dealroom-co/', 'https://linkedin.com/company/dealroom-co'),
            ('https://www.linkedin.com/company/upjers-gmbh-&-co.-kg', 'https://linkedin.com/company/upjers-gmbh-&-co.-kg'),
            ('https://www.linkedin.com/company/magis_official', 'https://linkedin.com/company/magis_official'),
            ('https://www.linkedin.com/company/cake-–-ridecake.com/', 'https://linkedin.com/company/cake-–-ridecake.com'),
            ('https://www.linkedin.com/company/brigham-and-women%27s-hospital/', 'https://linkedin.com/company/brigham-and-women%27s-hospital'),
            ('https://www.linkedin.com/school/linkedinschool/', 'https://linkedin.com/company/linkedinschool'),
            ('https://www.linkedin.com/school/linkedinschool', 'https://linkedin.com/company/linkedinschool'),
            ('http://www.linkedin.com/school/linkedinschool/', 'https://linkedin.com/company/linkedinschool'),
            ('https://linkedin.com/school/linkedinschool/', 'https://linkedin.com/company/linkedinschool'),
            ('https://www.linkedin.com/school/stanford-university/', 'https://linkedin.com/company/stanford-university'),
            ('https://www.linkedin.com/school/mit/', 'https://linkedin.com/company/mit'),
        ]
        
        for source, expected in company_test_cases:
            assert sl.is_valid("linkedin", source) is True, f"URL should be valid: {source}"
            result = sl.sanitize("linkedin", source)
            assert result == expected, f"Expected {expected}, got {result} for {source}"

