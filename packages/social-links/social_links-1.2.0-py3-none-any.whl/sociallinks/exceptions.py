"""Custom exceptions for the sociallinks library.

This module defines all custom exceptions used throughout the social-links
library. All exceptions inherit from `SocialLinksError`, allowing
you to catch all social-links related errors with a single exception handler.
"""

class SocialLinksError(Exception):
    """Base exception for all social-links errors.
    
    All custom exceptions in the social-links library inherit from this class,
    allowing you to catch all social-links related errors with a single
    exception handler.
    """
    pass


# ─────────────────────────────
# Platform-related errors
# ─────────────────────────────

class PlatformError(SocialLinksError):
    """Base exception for platform-related errors.
    
    This exception serves as the base class for all errors related to platform
    management, including platform registration, configuration, and lookup.
    All platform-specific errors inherit from this class.
    """
    pass


class PlatformNotFoundError(PlatformError):
    """Raised when a platform is not found.
    
    This exception is raised when attempting to access, modify, or delete a
    platform that does not exist in the platform registry.
    """
    pass


class PlatformAlreadyExistsError(PlatformError):
    """Raised when attempting to create a platform that already exists.
    
    This exception is raised when trying to register a platform with a name
    that is already in use. To replace an existing platform, use the ``override=True``
    parameter with `SocialLinks.set_platform` or `SocialLinks.set_platforms`.
    """
    pass


class InvalidPlatformError(PlatformError):
    """Raised when a platform has an invalid configuration.
    
    This exception is raised when a platform configuration is missing required
    fields or has invalid structure. A valid platform entry must be a list
    of dictionaries, each containing both `patterns` and `sanitized` keys.
    Entries missing either field are skipped, but at least one complete entry
    is required for the platform to be valid.
    """
    pass


class InvalidPlatformRegexError(InvalidPlatformError):
    """Raised when a platform defines an invalid regex pattern.
    
    This exception is raised when a regex pattern in a platform configuration
    cannot be compiled, typically due to syntax errors in the pattern string.
    """
    pass


# ─────────────────────────────
# URL parsing / matching errors
# ─────────────────────────────

class URLParsingError(SocialLinksError):
    """Base exception for URL parsing and matching errors.
    
    This exception serves as the base class for all errors related to URL
    parsing, validation, and matching operations. All URL-related errors
    inherit from this class.
    """
    pass


class URLMismatchError(URLParsingError):
    """Raised when a URL does not match the expected platform pattern.
    
    This exception is raised when attempting to validate or sanitize a URL
    that doesn't match any of the patterns defined for the specified platform.
    """
    pass


class PlatformIDExtractionError(URLParsingError):
    """Raised when a platform identifier cannot be extracted from a URL.
    
    This exception is raised when a URL matches a platform pattern but the
    platform identifier (username, ID, etc.) cannot be extracted, typically
    due to a missing or incorrectly named capture group in the regex pattern.
    """
    pass


