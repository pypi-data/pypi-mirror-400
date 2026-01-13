import re
from typing import Dict, List, Optional, Any, Tuple
from sociallinks.constants import PlatformEntry, PlatformEntries
from sociallinks.platforms import PREDEFINED_PLATFORMS
from sociallinks.exceptions import (
    PlatformNotFoundError,
    PlatformAlreadyExistsError,
    InvalidPlatformError,
    InvalidPlatformRegexError,
    PlatformIDExtractionError,
    URLMismatchError,
)


class SocialLinks:
    """Social Media URL Sanitizer and Validator.

    A lightweight, zero-dependency library for detecting, validating, and
    sanitizing social media profile URLs. Supports 50+ predefined platforms
    out of the box with automatic URL normalization and username extraction.

    The class uses regex patterns to match URLs against platform-specific
    formats and can normalize them to canonical forms. It also supports
    custom platform definitions for extensibility.

    Attributes:
        platforms: Dictionary of platform configurations.
        regex_flags: Regex flags used for pattern compilation.

    Examples:
        Basic usage with predefined platforms:

        >>> sl = SocialLinks()
        >>> sl.detect_platform("https://linkedin.com/in/johndoe")
        'linkedin'
        >>> sl.sanitize("linkedin", "https://www.linkedin.com/in/johndoe/")
        'https://linkedin.com/in/johndoe'

        Custom platforms:

        >>> sl = SocialLinks(use_predefined_platforms=False)
        >>> custom = [{"patterns": [r"https?://example.com/(?P<id>\\w+)"],
        ...            "sanitized": "https://example.com/{id}"}]
        >>> sl.set_platform("example", custom)
    """

    def __init__(
        self,
        use_predefined_platforms: bool = True,
        regex_flags: int = re.IGNORECASE,
    ):
        """Initialize the SocialLinks instance.

        Args:
            use_predefined_platforms: If True, loads 50+ predefined social
                media platforms (LinkedIn, GitHub, Twitter/X, etc.). If False,
                starts with an empty platform list. Defaults to True.
            regex_flags: Regex flags to use for pattern compilation. Defaults
                to `re.IGNORECASE`. Can be combined with other flags like
                `re.MULTILINE` using bitwise OR (|).

        Examples:
            >>> # Use predefined platforms (default)
            >>> sl = SocialLinks()
            >>> len(sl.list_platforms()) > 50
            True

            >>> # Start with empty platform list
            >>> sl = SocialLinks(use_predefined_platforms=False)
            >>> sl.list_platforms()
            []

            >>> # Use custom regex flags
            >>> import re
            >>> sl = SocialLinks(regex_flags=re.IGNORECASE | re.MULTILINE)
        """
        self.platforms: PlatformEntries = {}
        self._compiled: Dict[str, List[Tuple[re.Pattern, str]]] = {}
        self.regex_flags: int = regex_flags

        if use_predefined_platforms:
            self.platforms.update(PREDEFINED_PLATFORMS)

        # Compile all
        for name, data in self.platforms.items():
            self._compile_platform(name, data)

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    def _compile_platform(self, name: str, data: PlatformEntry) -> None:
        """Compile regex patterns for a platform.

        Internal method that compiles all regex patterns for a platform
        and stores them with their sanitized templates.

        Args:
            name: Platform name.
            data: Platform configuration.

        Raises:
            InvalidPlatformError: If no valid patterns are found.
            InvalidPlatformRegexError: If any regex pattern is invalid.
        """
        compiled_entries: List[Tuple[re.Pattern, str]] = []

        for entry in data:
            if not isinstance(entry, dict):
                continue

            patterns = entry.get("patterns")
            sanitized = entry.get("sanitized")

            if not patterns or not sanitized:
                continue

            for p in (patterns if isinstance(patterns, list) else [patterns]):
                try:
                    compiled_entries.append(
                        (re.compile(p, flags=self.regex_flags), sanitized)
                    )
                except re.error as e:
                    raise InvalidPlatformRegexError(
                        f"Invalid regex pattern for platform '{name}': {p}"
                    ) from e

        if not compiled_entries:
            raise InvalidPlatformError(f"Platform '{name}' has no valid patterns or templates.")

        self._compiled[name] = compiled_entries

    @staticmethod
    def _extract_id(match: re.Match) -> Optional[str]:
        """Extract platform identifier from a regex match.

        Attempts to extract the identifier using a named group "id",
        or falls back to the first non-empty capturing group.

        Args:
            match: Regex match object.

        Returns:
            Extracted identifier string, or None if not found.
        """
        if "id" in match.groupdict() and match.group("id"):
            return match.group("id")

        for g in match.groups():
            if g:
                return g
        return None

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def detect_platform(self, url: str) -> Optional[str]:
        """Detect the social media platform from a URL.

        Analyzes the provided URL against all registered platform patterns
        and returns the first matching platform name. The URL is automatically
        stripped of leading/trailing whitespace before matching.

        Args:
            url: The URL or username to analyze. Can be a full URL
                (e.g., "https://linkedin.com/in/johndoe") or just a username
                (e.g., "johndoe"). Whitespace is automatically stripped.

        Returns:
            The platform name (e.g., "linkedin", "github", "x") if detected,
            None if no platform matches.

        Raises:
            TypeError: If url is not a string.

        Examples:
            >>> sl = SocialLinks()
            >>> sl.detect_platform("https://linkedin.com/in/johndoe")
            'linkedin'
            >>> sl.detect_platform("https://github.com/username")
            'github'
            >>> sl.detect_platform("https://x.com/username")
            'x'
            >>> sl.detect_platform("johndoe")  # Username only, no URL
            None
            >>> sl.detect_platform("https://example.com")  # Unknown platform
            None
            >>> sl.detect_platform("  https://instagram.com/user  ")  # Whitespace handled
            'instagram'
        """
        if not isinstance(url, str):
            raise TypeError(f"url must be str, not {type(url).__name__}")
        
        u = url.strip()
        if not u:
            return None
        
        for name, entries in self._compiled.items():
            if any(pattern.search(u) for pattern, _ in entries):
                return name
        return None

    def is_valid(self, platform_name: str, url: str) -> bool:
        """Validate a URL against a specific platform.

        Checks if the provided URL matches any of the patterns defined for
        the specified platform. The URL is automatically stripped of
        leading/trailing whitespace before validation.

        Args:
            platform_name: The name of the platform to validate against
                (e.g., "linkedin", "github", "x").
            url: The URL to validate. Can be a full URL or just a username.
                Whitespace is automatically stripped.

        Returns:
            True if the URL matches the platform's patterns, False otherwise.
            Also returns False if the platform doesn't exist.

        Raises:
            TypeError: If platform_name or url is not a string.

        Examples:
            >>> sl = SocialLinks()
            >>> sl.is_valid("linkedin", "https://www.linkedin.com/in/johndoe/")
            True
            >>> sl.is_valid("linkedin", "https://github.com/username")
            False
            >>> sl.is_valid("github", "https://github.com/username")
            True
            >>> sl.is_valid("unknown_platform", "https://example.com")
            False
            >>> sl.is_valid("linkedin", "johndoe")  # Username only
            False
        """
        if not isinstance(platform_name, str):
            raise TypeError(f"platform_name must be str, not {type(platform_name).__name__}")
        if not isinstance(url, str):
            raise TypeError(f"url must be str, not {type(url).__name__}")
        
        entries = self._compiled.get(platform_name)
        if not entries:
            return False
        
        u = url.strip()
        if not u:
            return False
        
        return any(pattern.search(u) for pattern, _ in entries)

    def sanitize(self, platform_name: str, url: str) -> str:
        """Sanitize a URL to its canonical format for a specific platform.

        Normalizes a URL to the canonical format defined for the platform.
        Extracts the platform-specific identifier (username, profile ID, etc.)
        from the URL and formats it according to the platform's sanitized
        template. The URL is automatically stripped of leading/trailing
        whitespace before processing.

        Args:
            platform_name: The name of the platform (e.g., "linkedin",
                "github", "x").
            url: The URL to sanitize. Must match one of the platform's
                patterns. Whitespace is automatically stripped.

        Returns:
            The sanitized URL in canonical format for the platform.

        Raises:
            TypeError: If platform_name or url is not a string.
            PlatformNotFoundError: If the platform doesn't exist.
            URLMismatchError: If the URL doesn't match any of the platform's
                patterns or if the URL is empty.
            PlatformIDExtractionError: If the platform identifier cannot be
                extracted from the URL.

        Examples:
            >>> sl = SocialLinks()
            >>> sl.sanitize("linkedin", "https://www.linkedin.com/in/johndoe/")
            'https://linkedin.com/in/johndoe'
            >>> sl.sanitize("github", "http://www.github.com/username")
            'https://github.com/username'
            >>> sl.sanitize("x", "https://twitter.com/username")
            'https://x.com/username'
            >>> sl.sanitize("linkedin", "https://linkedin.com/in/john-doe-123")
            'https://linkedin.com/in/john-doe-123'
        """
        if not isinstance(platform_name, str):
            raise TypeError(f"platform_name must be str, not {type(platform_name).__name__}")
        if not isinstance(url, str):
            raise TypeError(f"url must be str, not {type(url).__name__}")
        
        entries = self._compiled.get(platform_name)
        if not entries:
            raise PlatformNotFoundError(f"Unknown platform: {platform_name}")

        u = url.strip()
        if not u:
            raise URLMismatchError("URL cannot be empty")
        
        for pattern, sanitized in entries:
            m = pattern.search(u)
            if m:
                pid = self._extract_id(m)
                if not pid:
                    raise PlatformIDExtractionError("Could not extract platform ID")
                pid = pid.strip().rstrip("/")
                return sanitized.format(id=pid)

        raise URLMismatchError(f"URL does not match platform '{platform_name}'")

    # ------------------------------------------------------------------
    # Platform CRUD (single + bulk)
    # ------------------------------------------------------------------

    def set_platform(self, name: str, data: PlatformEntry, *, override: bool = False) -> None:
        """Add or update a platform configuration.

        Registers a new platform. If the platform already exists, updates it
        only when override=True (default behavior raises an error). The platform
        patterns are compiled immediately and made available for use.

        Args:
            name: The name of the platform (e.g., "custom_platform").
            data: Platform configuration as a list of dictionaries. Each
                dictionary should contain:
                - "patterns": A regex pattern string or list of patterns
                  that match URLs for this platform. Patterns should use
                  named groups like `(?P<id>...)` to capture identifiers.
                - "sanitized": A template string for the canonical URL format,
                  using `{id}` as a placeholder for the extracted identifier.
            override: If False (default), raises an error if the platform
                already exists. If True, replaces the existing platform
                configuration.

        Raises:
            PlatformAlreadyExistsError: If the platform already exists and
                override is False.
            InvalidPlatformError: If the platform configuration is invalid
                (no valid patterns or templates).
            InvalidPlatformRegexError: If any regex pattern is invalid.

        Examples:
            >>> sl = SocialLinks(use_predefined_platforms=False)
            >>> custom = [{
            ...     "patterns": [
            ...         r"https?://(www\\.)?example\\.com/(?P<id>[A-Za-z0-9_]+)/?$",
            ...         r"^(?P<id>[A-Za-z0-9_]+)$"
            ...     ],
            ...     "sanitized": "https://example.com/{id}"
            ... }]
            >>> sl.set_platform("example", custom)
            >>> sl.detect_platform("https://example.com/user123")
            'example'
            >>> sl.sanitize("example", "https://example.com/user123")
            'https://example.com/user123'

            >>> # Update existing platform
            >>> sl.set_platform("example", custom, override=True)
        """
        exists = name in self.platforms
        if exists and not override:
            raise PlatformAlreadyExistsError(f"Platform '{name}' already exists. Use override=True.")

        self.platforms[name] = data
        self._compile_platform(name, data)

    def delete_platform(self, name: str) -> None:
        """Delete a platform configuration.

        Removes a platform from the registry. The platform will no longer
        be available for detection, validation, or sanitization.

        Args:
            name: The name of the platform to delete.

        Raises:
            PlatformNotFoundError: If the platform doesn't exist.

        Examples:
            >>> sl = SocialLinks()
            >>> "linkedin" in sl.list_platforms()
            True
            >>> sl.delete_platform("linkedin")
            >>> "linkedin" in sl.list_platforms()
            False
        """
        if name not in self.platforms:
            raise PlatformNotFoundError(f"Platform '{name}' not found")
        del self.platforms[name]
        self._compiled.pop(name, None)

    def set_platforms(self, platforms: PlatformEntries, *, override: bool = False) -> None:
        """Add or update multiple platform configurations at once.

        Bulk operation to register multiple platforms. If any platform already
        exists, updates occur only when override=True (default behavior raises
        an error). This is more efficient than calling `set_platform()` multiple
        times.

        Args:
            platforms: Dictionary mapping platform names to their
                configurations. Each value should be a `PlatformEntry` (list
                of dictionaries with "patterns" and "sanitized" keys).
            override: If False (default), raises an error if any platform
                already exists. If True, replaces existing platform
                configurations.

        Raises:
            PlatformAlreadyExistsError: If any platform already exists and
                override is False.
            InvalidPlatformError: If any platform configuration is invalid.
            InvalidPlatformRegexError: If any regex pattern is invalid.

        Examples:
            >>> sl = SocialLinks(use_predefined_platforms=False)
            >>> new_platforms = {
            ...     "platform1": [{
            ...         "patterns": [r"https?://example1.com/(?P<id>\\w+)"],
            ...         "sanitized": "https://example1.com/{id}"
            ...     }],
            ...     "platform2": [{
            ...         "patterns": [r"https?://example2.com/(?P<id>\\w+)"],
            ...         "sanitized": "https://example2.com/{id}"
            ...     }]
            ... }
            >>> sl.set_platforms(new_platforms)
            >>> len(sl.list_platforms())
            2
        """
        if not override:
            conflicts = [name for name in platforms if name in self.platforms]
            if conflicts:
                raise PlatformAlreadyExistsError(f"Platforms already exist: {', '.join(conflicts)}")

        for name, data in platforms.items():
            self.set_platform(name, data, override=override)

    def delete_platforms(self, names: List[str]) -> None:
        """Delete multiple platform configurations at once.

        Bulk operation to remove multiple platforms. This is more efficient
        than calling `delete_platform()` multiple times.

        Args:
            names: List of platform names to delete.

        Raises:
            PlatformNotFoundError: If any of the specified platforms don't
                exist. The error message includes all missing platforms.

        Examples:
            >>> sl = SocialLinks()
            >>> sl.delete_platforms(["linkedin", "github"])
            >>> "linkedin" in sl.list_platforms()
            False
            >>> "github" in sl.list_platforms()
            False
        """
        missing = [n for n in names if n not in self.platforms]
        if missing:
            raise PlatformNotFoundError(f"Platforms not found: {', '.join(missing)}")
        for n in names:
            self.delete_platform(n)

    def clear_platforms(self) -> None:
        """Remove all platform configurations.

        Clears both the platform registry and compiled patterns. After calling
        this method, no platforms will be available until new ones are added.

        Examples:
            >>> sl = SocialLinks()
            >>> len(sl.list_platforms()) > 0
            True
            >>> sl.clear_platforms()
            >>> sl.list_platforms()
            []
        """
        self.platforms.clear()
        self._compiled.clear()

    def get_platform(self, name: str) -> PlatformEntry:
        """Get the configuration for a specific platform.

        Retrieves the platform configuration, which can be useful for
        inspection or modification before re-adding with `set_platform()`.

        Args:
            name: The name of the platform.

        Returns:
            The platform configuration as a `PlatformEntry` (list of
            dictionaries with "patterns" and "sanitized" keys).

        Raises:
            PlatformNotFoundError: If the platform doesn't exist.

        Examples:
            >>> sl = SocialLinks()
            >>> config = sl.get_platform("github")
            >>> isinstance(config, list)
            True
            >>> "patterns" in config[0]
            True
            >>> "sanitized" in config[0]
            True
        """
        if name not in self.platforms:
            raise PlatformNotFoundError(f"Platform '{name}' not found")
        return self.platforms[name]

    def list_platforms(self) -> List[str]:
        """List all registered platform names.

        Returns a list of all platform names that are currently registered
        and available for use.

        Returns:
            A list of platform names (strings) in no particular order.

        Examples:
            >>> sl = SocialLinks()
            >>> platforms = sl.list_platforms()
            >>> isinstance(platforms, list)
            True
            >>> "linkedin" in platforms
            True
            >>> "github" in platforms
            True
            >>> len(platforms) > 50
            True
        """
        return list(self.platforms.keys())
