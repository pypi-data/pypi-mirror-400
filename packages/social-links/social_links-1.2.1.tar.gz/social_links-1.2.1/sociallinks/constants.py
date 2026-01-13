"""Constants and type aliases for the sociallinks library.

This module provides:
- Type aliases for platform configuration structures
- Common regex patterns for matching profile IDs and phone numbers

These constants are used internally by the `SocialLinks` class and can
also be imported for use in custom platform definitions.
"""
from typing import List, Dict, Any

# ----------------------------------------------------------------------
# Type Aliases
# ----------------------------------------------------------------------

PlatformEntry = List[Dict[str, Any]]
"""Type alias for a platform configuration entry.

A platform entry is a list of dictionaries, where each dictionary contains
platform configuration such as patterns and sanitized URL templates.
A platform can have multiple configuration variants (e.g., different URL
patterns for profiles vs. companies).

Each dictionary in the list should contain:
- ``patterns``: A list of regex pattern strings that match URLs for this platform
- ``sanitized``: A template string for the sanitized URL format

Note: Entries missing either ``patterns`` or ``sanitized`` will be skipped during
compilation. At least one complete entry (with both fields) is required for a
valid platform configuration.

Example:
    ```python
    entry: PlatformEntry = [
        {
            "patterns": [r"https?://example.com/(?P<id>\\w+)"],
            "sanitized": "https://example.com/{id}"
        }
    ]
    ```
"""

PlatformEntries = Dict[str, PlatformEntry]
"""Type alias for a collection of platform configurations.

A dictionary mapping platform names (strings) to their configuration entries.
This is the structure used internally by `SocialLinks` to store all
registered platforms.

Example:
    ```python
    platforms: PlatformEntries = {
        "example": [
            {
                "patterns": [r"https?://example.com/(?P<id>\\w+)"],
                "sanitized": "https://example.com/{id}"
            }
        ],
        "another": [
            {
                "patterns": [r"https?://another.com/user/(?P<id>\\w+)"],
                "sanitized": "https://another.com/user/{id}"
            }
        ]
    }
    ```
"""


# ----------------------------------------------------------------------
# Common ID regex patterns
# ----------------------------------------------------------------------

PROFILE_ID = r"(?P<id>[A-Za-z0-9_.-]+)"
"""Standard profile ID regex pattern.

Matches alphanumeric characters, underscore, period, and hyphen.

Used for most social media platforms with standard username formats.

Example matches:
    - ``john_doe``
    - ``user123``
    - ``my.profile``
    - ``user-name``
"""

PROFILE_ID_AT = r"(?P<id>@?[A-Za-z0-9_.-]+)"
"""Profile ID regex pattern with optional @ prefix.

Matches profile IDs that may optionally start with an @ symbol.

Commonly used for platforms like YouTube channels.

Example matches:
    - ``@channel``
    - ``channel``
    - ``@user_name``
"""

PROFILE_ID_UNICODE = r"(?P<id>[\w&%'–®\.-]+)"
"""Profile ID regex pattern supporting Unicode characters.

Matches Unicode word characters (via ``\w``, which includes Unicode letters
and digits in Python 3), plus special characters including:
- Ampersand (&)
- Percent (%)
- Apostrophe (')
- En dash (–)
- Registered trademark (®)
- Period (.)
- Hyphen (-)

Used for platforms like LinkedIn that support international characters.

Example matches:
    - ``peter-müller-81a8``
    - ``user&co``
    - ``name's-profile``
    - ``josé-garcía``
"""

PROFILE_ID_EXTENDED = r"(?P<id>-?[A-Za-z0-9_@=.\-]+)"
"""Extended profile ID regex pattern with additional character support.

Supports:
- Optional leading hyphen (for Telegram groups, e.g., ``-123456789``)
- @ symbol (for platforms like Flickr)
- Equals sign (for Douyin base64 encoded IDs)
- Period (.)
- Standard alphanumeric characters, underscore, and hyphen

Example matches:
    - ``-123456789`` (Telegram group)
    - ``@username`` (Flickr)
    - ``base64==`` (Douyin)
    - ``normal_user``
"""

PHONE_NUMBER = r"(?P<id>\+?[0-9]+)"
"""Phone number regex pattern.

Matches phone numbers that may optionally start with a + sign.

Primarily used for WhatsApp platform.

Example matches:
    - ``+1234567890``
    - ``1234567890``
    - ``+441234567890``
"""

