"""Tests for Apple Music platform."""
import pytest


class TestAppleMusic:
    """Test Apple Music platform"""

    def test_apple_music(self, sl):
        """Test Apple Music platform"""
        artist_id = "136975"
        assert sl.detect_platform(f"https://music.apple.com/artist/{artist_id}") == "apple_music"
        assert sl.is_valid("apple_music", f"https://music.apple.com/artist/{artist_id}") is True
        assert sl.sanitize("apple_music", f"https://music.apple.com/artist/{artist_id}") == f"https://music.apple.com/artist/{artist_id}"
        
        assert sl.is_valid("apple_music", artist_id) is True
        assert sl.sanitize("apple_music", artist_id) == f"https://music.apple.com/artist/{artist_id}"
        
        test_cases = [
            ('https://music.apple.com/us/artist/the-beatles/136975', 'https://music.apple.com/artist/136975'),
            ('https://music.apple.com/us/artist/beatles/136975', 'https://music.apple.com/artist/136975'),
            ('https://music.apple.com/artist/beatles/136975', 'https://music.apple.com/artist/136975'),
            ('https://music.apple.com/artist/136975', 'https://music.apple.com/artist/136975'),
            ('https://itunes.apple.com/us/artist/id136975', 'https://music.apple.com/artist/136975'),
        ]
        for source, expected in test_cases:
            assert sl.is_valid("apple_music", source) is True
            assert sl.sanitize("apple_music", source) == expected

