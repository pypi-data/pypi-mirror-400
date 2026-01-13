"""Pytest configuration and fixtures for platform tests."""
import pytest
from sociallinks.core import SocialLinks


@pytest.fixture
def sl():
    """Create a SocialLinks instance with predefined platforms."""
    return SocialLinks()

