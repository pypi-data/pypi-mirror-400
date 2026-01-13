# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.1]

### Added

- Interactive demo page in documentation with Pyodide integration
  - Browser-based testing interface for detecting platforms, validating URLs, and sanitizing links
  - No installation required - runs entirely in the browser
  - Real-time platform detection and validation feedback
- Demo badge in README linking to interactive demo
- Prominent callout in README highlighting the interactive demo feature

### Changed

- Enhanced README visibility for demo page with badge and callout placement
- Improved user experience with easier access to interactive testing

## [1.2.0]

### Added

- Support for 28 new social media platforms:
  - **Music & Audio**: Apple Music, Bandcamp
  - **Video Platforms**: Douyin, Kuaishou, Vimeo
  - **Social Networks**: Bluesky, Discord, Reddit, Snapchat, Tumblr, Threads (Instagram)
  - **Professional & Business**: Crunchbase, GitLab, HackerNews, ProductHunt, Wellfound (AngelList)
  - **E-commerce & Marketplaces**: Etsy, Gumroad
  - **Content & Publishing**: Hashnode, Slideshare
  - **Messaging & Communication**: Signal, WeChat, WhatsApp
  - **Photo & Media**: Flickr, Gravatar
  - **Gaming**: Steam
  - **Q&A & Forums**: Quora
  - **Chinese Platforms**: Weibo
- `InvalidPlatformRegexError` exception for handling invalid regex patterns in platform configurations
- `constants.py` module with reusable regex patterns and type aliases for platform configuration
- Comprehensive API reference documentation
- Function and constant docstrings throughout the codebase
- Roadmap section in README
- Google verification key for documentation
- SEO meta tags and title templates for documentation pages
- Common test patterns module for parametrized testing across platforms

### Changed

- Enhanced platform pattern matching:
  - LinkedIn: Added support for school URLs and improved pattern matching with `%` character support
  - Reddit: Added support for subreddit URLs and `u/` prefix format
  - Telegram: Enhanced with additional URL patterns
  - Spotify: Added support for artist profile URLs and improved user profile patterns
  - Quora: Added support for Unicode characters in profile URLs
  - Substack: Updated URL patterns for better matching
  - WhatsApp: Added support for send URL format
  - YouTube: Fixed channel pattern matching
- Refactored exception hierarchy:
  - Introduced `PlatformError` as base class for platform-related errors
  - Introduced `URLParsingError` as base class for URL parsing errors
  - Improved error categorization and inheritance structure
- Refactored test suite:
  - Split monolithic `test_platforms.py` into individual platform-specific test files
  - Added `conftest.py` for shared test fixtures
  - Parametrized common test cases (www, http, trailing_slash) for better coverage
- Updated README:
  - Formatted predefined platforms in a table for better readability
  - Removed outdated error handling section
- Enhanced `pyproject.toml` with improved keywords and metadata
- Improved documentation structure with better organization and SEO optimization

### Fixed

- Fixed YouTube channel pattern matching issues
- Fixed sanitization pattern edge cases
- Fixed documentation bugs

## [1.1.0]

### Added

- MkDocs documentation setup with Material theme
- Comprehensive Contributing Guide (CONTRIBUTING.md) with development setup instructions
- GitHub Actions workflow for automated documentation deployment
- Documentation badge in README linking to hosted documentation
- Links section in README with all project resources
- Added py.typed file for type hinting

### Changed

- Updated README with clickable links for all 25+ supported platforms
- Enhanced README structure with Changelog, Contributing, and Support sections
- Improved documentation organization with dedicated docs/ directory


## [1.0.0]

### Added

- Initial release of social-links
- `SocialLinks` class for detecting and sanitizing social media URLs
- `detect_platform()` method for automatically detecting platform from URL
- `is_valid()` method for validating URLs against specific platforms
- `sanitize()` method for normalizing URLs to canonical format
- Platform management methods:
  - `set_platform()` - Add or override a single platform
  - `delete_platform()` - Remove a single platform
  - `set_platforms()` - Bulk add/override platforms
  - `delete_platforms()` - Bulk remove platforms
  - `clear_platforms()` - Remove all platforms
  - `get_platform()` - Retrieve platform configuration
  - `list_platforms()` - List all registered platforms
- Support for 25+ predefined social media platforms:
  - behance, dev_to, dribbble, exercism, facebook, github, instagram, keybase, lemmy_world, linkedin, linktree, mastodon, medium, patreon, pinterest, soundcloud, spotify, stackoverflow, substack, telegram, tiktok, twitch, vk, x (Twitter), youtube
- Custom regex pattern support for flexible URL matching
- Multiple pattern support per platform
- Automatic ID extraction from URLs
- Support for various URL formats (with/without protocol, www, mobile variants)
- Customizable regex flags for pattern matching
- Comprehensive error handling with custom exceptions:
  - `SocialLinksError` - Base exception
  - `PlatformNotFoundError` - Platform not found
  - `PlatformAlreadyExistsError` - Platform already exists
  - `InvalidPlatformError` - Invalid platform configuration
  - `PlatformIDExtractionError` - Failed to extract platform ID
  - `URLMismatchError` - URL doesn't match platform pattern
- Full test coverage with comprehensive test suite

### Features

- Zero external dependencies
- Python 3.8+ compatibility
- Case-insensitive URL matching (configurable)
- Support for username-only input (without full URLs)
- Automatic @ symbol handling
- URL normalization and sanitization

[1.2.1]: https://github.com/ysskrishna/social-links/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/ysskrishna/social-links/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/ysskrishna/social-links/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/ysskrishna/social-links/releases/tag/v1.0.0
