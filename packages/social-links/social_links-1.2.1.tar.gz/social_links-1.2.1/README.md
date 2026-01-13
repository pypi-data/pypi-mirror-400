# Social Links

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Tests](https://github.com/ysskrishna/social-links/actions/workflows/test.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
[![PyPI](https://img.shields.io/pypi/v/social-links)](https://pypi.org/project/social-links/)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/social-links?period=total&units=INTERNATIONAL_SYSTEM&left_color=GREY&right_color=BLUE&left_text=downloads)](https://pepy.tech/projects/social-links)
[![Documentation](https://img.shields.io/badge/docs-ysskrishna.github.io%2Fsocial--links-blue.svg)](https://ysskrishna.github.io/social-links/)
[![Interactive Demo](https://img.shields.io/badge/demo-Try%20it%20now!-green.svg)](https://ysskrishna.github.io/social-links/demo/)

A lightweight, zero-dependency Python library for detecting, validating, and sanitizing social media profile URLs. Supports 50+ platforms out of the box with automatic URL normalization, username extraction, and customizable regex patterns for extensibility.

> 🚀 **Try it interactively in your browser!** Test the library with our [Interactive Demo](https://ysskrishna.github.io/social-links/demo/) - no installation required.

![OG Image](https://raw.githubusercontent.com/ysskrishna/social-links/main/media/og.png)

## Features

- 🔍 **Auto-detect** social media platforms from URLs
- ✅ **Validate** URLs against specific platforms
- 🧹 **Sanitize** URLs to canonical format
- 🎯 **50+ predefined platforms** (LinkedIn, GitHub, Twitter/X, Facebook, Instagram, YouTube, and more)
- 🔧 **Customizable** - Add your own platforms with regex patterns
- 🚀 **Zero dependencies** - Pure Python, no external libraries

## Installation

```bash
pip install social-links
```

Or using `uv`:

```bash
uv pip install social-links
```

## Quick Start

```python
from sociallinks import SocialLinks

# Initialize with predefined platforms
sl = SocialLinks()

# Detect platform from URL
platform = sl.detect_platform("https://www.linkedin.com/in/ysskrishna/")
print(platform)  # "linkedin"

# Validate URL for a specific platform
is_valid = sl.is_valid("linkedin", "https://www.linkedin.com/in/ysskrishna/")
print(is_valid)  # True

# Sanitize URL to canonical format
sanitized = sl.sanitize("linkedin", "https://www.linkedin.com/in/ysskrishna/")
print(sanitized)  # "https://linkedin.com/in/ysskrishna"
```

## Supported Platforms

The library comes with 50+ predefined platforms:

| Predefined Platforms| | |
|---|---|---|
| [Apple Music](https://music.apple.com) | [Bandcamp](https://bandcamp.com) | [Behance](https://behance.net) |
| [Bluesky](https://bsky.app) | [Crunchbase](https://crunchbase.com) | [Dev.to](https://dev.to) |
| [Discord](https://discord.com) | [Douyin](https://douyin.com) | [Dribbble](https://dribbble.com) |
| [Etsy](https://etsy.com) | [Exercism](https://exercism.io) | [Facebook](https://facebook.com) |
| [Flickr](https://flickr.com) | [GitHub](https://github.com) | [GitLab](https://gitlab.com) |
| [Gravatar](https://gravatar.com) | [Gumroad](https://gumroad.com) | [Hacker News](https://news.ycombinator.com) |
| [Hashnode](https://hashnode.com) | [Instagram](https://instagram.com) | [Keybase](https://keybase.io) |
| [Kuaishou](https://kuaishou.com) | [Lemmy World](https://lemmy.world) | [LinkedIn](https://linkedin.com) (personal & company) |
| [Linktree](https://linktr.ee) | [Mastodon](https://mastodon.social) | [Medium](https://medium.com) |
| [Patreon](https://patreon.com) | [Pinterest](https://pinterest.com) | [Product Hunt](https://producthunt.com) |
| [Quora](https://quora.com) | [Reddit](https://reddit.com) | [Signal](https://signal.me) |
| [SlideShare](https://slideshare.net) | [Snapchat](https://snapchat.com) | [SoundCloud](https://soundcloud.com) |
| [Spotify](https://spotify.com) | [Stack Overflow](https://stackoverflow.com) | [Steam](https://steamcommunity.com) |
| [Substack](https://substack.com) | [Telegram](https://telegram.org) | [Threads](https://threads.net) |
| [TikTok](https://tiktok.com) | [Tumblr](https://tumblr.com) | [Twitch](https://twitch.tv) |
| [Vimeo](https://vimeo.com) | [VK](https://vk.com) | [WeChat](https://weixin.qq.com) |
| [Weibo](https://weibo.com) | [Wellfound (AngelList)](https://wellfound.com) | [WhatsApp](https://whatsapp.com) |
| [X (Twitter)](https://x.com) | [YouTube](https://youtube.com) | |

## Usage Examples

### Detect Platform

```python
sl = SocialLinks()

# Detect from full URL
sl.detect_platform("https://github.com/ysskrishna")  # "github"
sl.detect_platform("https://x.com/ysskrishna")      # "x"
sl.detect_platform("https://example.com")         # None

# Works with various URL formats
sl.detect_platform("http://linkedin.com/in/ysskrishna")
sl.detect_platform("www.facebook.com/ysskrishna")
sl.detect_platform("  https://instagram.com/ysskrishna  ")  # Handles whitespace
```

### Validate URLs

```python
sl = SocialLinks()

# Validate against specific platform
sl.is_valid("linkedin", "https://www.linkedin.com/in/ysskrishna/")  # True
sl.is_valid("linkedin", "https://example.com")                   # False
sl.is_valid("github", "https://github.com/ysskrishna")             # True
```

### Sanitize URLs

```python
sl = SocialLinks()

# Normalize to canonical format
sl.sanitize("linkedin", "https://www.linkedin.com/in/ysskrishna/")
# Returns: "https://linkedin.com/in/ysskrishna"

sl.sanitize("github", "http://www.github.com/ysskrishna")
# Returns: "https://github.com/ysskrishna"

sl.sanitize("x", "https://twitter.com/ysskrishna")
# Returns: "https://x.com/ysskrishna"
```

### Custom Platforms

```python
sl = SocialLinks(use_predefined_platforms=False)

# Add a custom platform
custom_platform = [{
    "patterns": [
        r"https?://(www\.)?example\.com/(?P<id>[A-Za-z0-9_]+)/?$",
        r"^(?P<id>[A-Za-z0-9_]+)$"  # Username-only pattern
    ],
    "sanitized": "https://example.com/{id}"
}]

sl.set_platform("example", custom_platform)

# Now you can use it
sl.detect_platform("https://example.com/user123")  # "example"
sl.sanitize("example", "https://example.com/user123")  # "https://example.com/user123"
```

### Platform Management

```python
sl = SocialLinks()

# List all platforms
platforms = sl.list_platforms()
# Returns: ["behance", "dev_to", "dribbble", ...]

# Get platform configuration
config = sl.get_platform("github")

# Add multiple platforms
new_platforms = {
    "platform1": [{
        "patterns": [r"https?://example1.com/(?P<id>\w+)"],
        "sanitized": "https://example1.com/{id}"
    }],
    "platform2": [{
        "patterns": [r"https?://example2.com/(?P<id>\w+)"],
        "sanitized": "https://example2.com/{id}"
    }]
}
sl.set_platforms(new_platforms, override=False)

# Delete platforms
sl.delete_platform("custom_platform")
sl.delete_platforms(["platform1", "platform2"])

# Clear all platforms
sl.clear_platforms()
```

### Custom Regex Flags

```python
import re
from sociallinks import SocialLinks

# Use custom regex flags
sl = SocialLinks(regex_flags=re.IGNORECASE | re.MULTILINE)
```

## Changelog

See [CHANGELOG.md](https://github.com/ysskrishna/social-links/blob/main/CHANGELOG.md) for a detailed list of changes and version history.

## Roadmap

The following improvements are planned for upcoming releases:

- [ ] Add method to configure custom sanitization patterns
- [ ] Create Streamlit demo application
- [ ] Integrate development tools (flake8, black, isort) for code quality
- [ ] Add code coverage reporting with pytest-cov
- [ ] Refactor platform entries using dataclasses for better structure
- [ ] Consider functional API alternative to SocialLinks class for simpler usage

## Contributing

Contributions are welcome! Please read our [Contributing Guide](https://github.com/ysskrishna/social-links/blob/main/CONTRIBUTING.md) for details on our code of conduct, development setup, and the process for submitting pull requests.

## Support

If you find this library useful, please consider:

- ⭐ **Starring** the repository on GitHub to help others discover it.

- 💖 **Sponsoring** to support ongoing maintenance and development.

[Become a Sponsor on GitHub](https://github.com/sponsors/ysskrishna) | [Support on Patreon](https://patreon.com/ysskrishna)

## Links

- **Documentation**: [ysskrishna.github.io/social-links](https://ysskrishna.github.io/social-links/)

- **Interactive Demo**: [ysskrishna.github.io/social-links/demo/](https://ysskrishna.github.io/social-links/demo/)

- **PyPI**: [pypi.org/project/social-links](https://pypi.org/project/social-links/)

- **Homepage**: [github.com/ysskrishna/social-links](https://github.com/ysskrishna/social-links)

- **Repository**: [github.com/ysskrishna/social-links.git](https://github.com/ysskrishna/social-links.git)

- **Issues**: [github.com/ysskrishna/social-links/issues](https://github.com/ysskrishna/social-links/issues)


## License

MIT License - see [LICENSE](https://github.com/ysskrishna/social-links/blob/main/LICENSE) file for details.

## Author

**Y. Siva Sai Krishna**

- GitHub: [@ysskrishna](https://github.com/ysskrishna)

- LinkedIn: [ysskrishna](https://linkedin.com/in/ysskrishna)
