from sociallinks.constants import (
    PROFILE_ID,
    PROFILE_ID_AT,
    PROFILE_ID_UNICODE,
    PROFILE_ID_EXTENDED,
    PHONE_NUMBER,
    PlatformEntries,
)

# ----------------------------------------------------------------------
# Predefined platforms
# ----------------------------------------------------------------------
PREDEFINED_PLATFORMS: PlatformEntries = {
    "behance": [
        {
            "patterns": [
                rf"https?://(www\.)?behance\.net/{PROFILE_ID}/?$",
                rf"^{PROFILE_ID}$"
            ],
            "sanitized": "https://behance.net/{id}"
        }
    ],
    "bluesky": [
        {
            "patterns": [
                rf"https?://(www\.)?bsky\.app/profile/{PROFILE_ID}/?$",
                rf"^@?{PROFILE_ID}$"
            ],
            "sanitized": "https://bsky.app/profile/{id}"
        }
    ],
    "crunchbase": [
        {
            "patterns": [
                rf"https?://(www\.)?crunchbase\.com/organization/{PROFILE_ID}/?$",
                rf"https?://(www\.)?crunchbase\.com/company/{PROFILE_ID}/?$",
            ],
            "sanitized": "https://www.crunchbase.com/organization/{id}"
        },
        {
            "patterns": [
                rf"https?://(www\.)?crunchbase\.com/person/{PROFILE_ID}/?$",
            ],
            "sanitized": "https://www.crunchbase.com/person/{id}"
        }
    ],
    "dev_to": [
        {
            "patterns": [
                rf"https?://(www\.)?dev\.to/{PROFILE_ID}/?$",
                rf"^{PROFILE_ID}$"
            ],
            "sanitized": "https://dev.to/{id}"
        }
    ],
    "discord": [
        {
            "patterns": [
                rf"https?://(www\.)?discord\.gg/{PROFILE_ID}/?$",
                rf"https?://(www\.)?discord\.com/invite/{PROFILE_ID}/?$",
                rf"^{PROFILE_ID}$"
            ],
            "sanitized": "https://discord.gg/{id}"
        }
    ],
    "douyin": [
        {
            "patterns": [
                rf"https?://(www\.)?douyin\.com/user/{PROFILE_ID_EXTENDED}/?$",
                rf"^{PROFILE_ID_EXTENDED}$"
            ],
            "sanitized": "https://www.douyin.com/user/{id}"
        }
    ],
    "dribbble": [
        {
            "patterns": [
                rf"https?://(www\.)?dribbble\.com/{PROFILE_ID}/?$",
                rf"^{PROFILE_ID}$"
            ],
            "sanitized": "https://dribbble.com/{id}"
        }
    ],
    "etsy": [
        {
            "patterns": [
                rf"https?://(www\.)?etsy\.com/shop/{PROFILE_ID}/?$",
                rf"^{PROFILE_ID}$"
            ],
            "sanitized": "https://etsy.com/shop/{id}"
        }
    ],
    "exercism": [
        {
            "patterns": [
                rf"https?://(www\.)?exercism\.io/profiles/{PROFILE_ID}/?$",
                rf"^{PROFILE_ID}$"
            ],
            "sanitized": "https://exercism.io/profiles/{id}"
        }
    ],
    "facebook": [
        {
            "patterns": [
                rf"https?://(www\.)?facebook\.com/{PROFILE_ID}/?$",
                rf"https?://m\.facebook\.com/{PROFILE_ID}/?$",
                rf"^{PROFILE_ID}$"
            ],
            "sanitized": "https://facebook.com/{id}"
        }
    ],
    "flickr": [
        {
            "patterns": [
                rf"https?://(www\.)?flickr\.com/people/{PROFILE_ID_EXTENDED}/?$",
                rf"^{PROFILE_ID_EXTENDED}$"
            ],
            "sanitized": "https://www.flickr.com/people/{id}"
        }
    ],
    "github": [
        {
            "patterns": [
                rf"https?://(www\.)?github\.com/{PROFILE_ID}/?$",
                rf"^{PROFILE_ID}$"
            ],
            "sanitized": "https://github.com/{id}"
        }
    ],
    "gitlab": [
        {
            "patterns": [
                rf"https?://(www\.)?gitlab\.com/{PROFILE_ID}/?$",
                rf"^{PROFILE_ID}$"
            ],
            "sanitized": "https://gitlab.com/{id}"
        }
    ],
    "gravatar": [
        {
            "patterns": [
                rf"https?://([a-z]{{2,3}}\.)?gravatar\.com/{PROFILE_ID}/?$",
                rf"^{PROFILE_ID}$"
            ],
            "sanitized": "https://gravatar.com/{id}"
        }
    ],
    "hackernews": [
        {
            "patterns": [
                rf"https?://(www\.)?news\.ycombinator\.com/user\?id={PROFILE_ID}/?$",
                rf"^{PROFILE_ID}$"
            ],
            "sanitized": "https://news.ycombinator.com/user?id={id}"
        }
    ],
    "instagram": [
        {
            "patterns": [
                rf"https?://(www\.)?instagram\.com/{PROFILE_ID}/?$",
                rf"https?://m\.instagram\.com/{PROFILE_ID}/?$",
                rf"^{PROFILE_ID}$"
            ],
            "sanitized": "https://instagram.com/{id}"
        }
    ],
    "keybase": [
        {
            "patterns": [
                rf"https?://(www\.)?keybase\.io/{PROFILE_ID}/?$",
                rf"^{PROFILE_ID}$"
            ],
            "sanitized": "https://keybase.io/{id}"
        }
    ],
    "kuaishou": [
        {
            "patterns": [
                rf"https?://(www\.)?kuaishou\.com/profile/{PROFILE_ID}/?$",
                rf"^{PROFILE_ID}$"
            ],
            "sanitized": "https://www.kuaishou.com/profile/{id}"
        }
    ],
    "lemmy_world": [
        {
            "patterns": [
                rf"https?://lemmy\.world/u/{PROFILE_ID}/?$",
                rf"^{PROFILE_ID}$"
            ],
            "sanitized": "https://lemmy.world/u/{id}"
        }
    ],
    "linkedin": [
        {
            "patterns": [
                # LinkedIn profile IDs can contain Unicode characters (e.g., ü in peter-müller-81a8)
                rf"https?://([a-z]{{2,3}}\.)?linkedin\.com/in/{PROFILE_ID_UNICODE}/?$",
                rf"https?://([a-z]{{2,3}}\.)?linkedin\.com/mwlite/in/{PROFILE_ID_UNICODE}/?$",
                rf"^{PROFILE_ID_UNICODE}$"
            ],
            "sanitized": "https://linkedin.com/in/{id}"
        },
        {
            "patterns": [
                
                rf"https?://(www\.)?linkedin\.com/company/{PROFILE_ID_UNICODE}/?$",
                rf"https?://(www\.)?linkedin\.com/school/{PROFILE_ID_UNICODE}/?$",
            ],
            "sanitized": "https://linkedin.com/company/{id}"
        }
    ],
    "wellfound": [
        {
            "patterns": [
                rf"https?://(www\.)?wellfound\.com/u/{PROFILE_ID}/?$",
                rf"https?://(www\.)?angel\.co/u/{PROFILE_ID}/?$",
                rf"^{PROFILE_ID}$"
            ],
            "sanitized": "https://wellfound.com/u/{id}"
        },
        {
            "patterns": [
                rf"https?://(www\.)?wellfound\.com/company/{PROFILE_ID}/?$",
                rf"https?://(www\.)?angel\.co/company/{PROFILE_ID}/?$",
                rf"https?://(www\.)?angel\.co/{PROFILE_ID}/?$"
            ],
            "sanitized": "https://wellfound.com/company/{id}"
        }
    ],
    "linktree": [
        {
            "patterns": [
                rf"https?://(www\.)?linktr\.ee/{PROFILE_ID}/?$",
                rf"^{PROFILE_ID}$"
            ],
            "sanitized": "https://linktr.ee/{id}"
        }
    ],
    "mastodon": [
        {
            "patterns": [
                rf"https?://(www\.)?mastodon\.social/@{PROFILE_ID}/?$",
                rf"https?://(www\.)?mstdn\.social/@{PROFILE_ID}/?$",
                rf"https?://(www\.)?mastodon\.world/@{PROFILE_ID}/?$",
                rf"^@?{PROFILE_ID}$"
            ],
            "sanitized": "https://mastodon.social/@{id}"
        }
    ],
    "medium": [
        {
            "patterns": [
                rf"https?://(www\.)?medium\.com/@{PROFILE_ID}/?$",
                rf"^@?{PROFILE_ID}$"
            ],
            "sanitized": "https://medium.com/@{id}"
        }
    ],
    "patreon": [
        {
            "patterns": [
                rf"https?://(www\.)?patreon\.com/{PROFILE_ID}/?$",
                rf"^{PROFILE_ID}$"
            ],
            "sanitized": "https://patreon.com/{id}"
        }
    ],
    "pinterest": [
        {
            "patterns": [
                rf"https?://([a-z]{{1,3}}\.)?pinterest\.com/{PROFILE_ID}/?$",
                rf"^{PROFILE_ID}$"
            ],
            "sanitized": "https://pinterest.com/{id}"
        }
    ],
    "quora": [
        {
            "patterns": [
                rf"https?://(www\.)?quora\.com/profile/{PROFILE_ID_UNICODE}/?$",
                rf"https?://(www\.)?quora\.com/{PROFILE_ID_UNICODE}/?$",
                rf"^{PROFILE_ID_UNICODE}$"
            ],
            "sanitized": "https://quora.com/profile/{id}"
        }
    ],
    "reddit": [
        {
            "patterns": [
                rf"https?://(www\.)?reddit\.com/user/{PROFILE_ID}/?$",
                rf"https?://(www\.)?reddit\.com/u/{PROFILE_ID}/?$",
                rf"https?://old\.reddit\.com/user/{PROFILE_ID}/?$",
                rf"https?://old\.reddit\.com/u/{PROFILE_ID}/?$",
                rf"^u/{PROFILE_ID}$",
                rf"^{PROFILE_ID}$"
            ],
            "sanitized": "https://reddit.com/user/{id}"
        },
        {
            "patterns": [
                rf"https?://(www\.)?reddit\.com/r/{PROFILE_ID}/?$",
                rf"https?://old\.reddit\.com/r/{PROFILE_ID}/?$",
                rf"^r/{PROFILE_ID}$"
            ],
            "sanitized": "https://reddit.com/r/{id}"
        }
    ],
    "signal": [
        {
            "patterns": [
                rf"https?://(www\.)?signal\.me/#p/{PROFILE_ID}/?$",
                rf"^{PROFILE_ID}$"
            ],
            "sanitized": "https://signal.me/#p/{id}"
        }
    ],
    "slideshare": [
        {
            "patterns": [
                rf"https?://(www\.)?slideshare\.net/{PROFILE_ID}/?$",
                rf"^{PROFILE_ID}$"
            ],
            "sanitized": "https://www.slideshare.net/{id}"
        }
    ],
    "snapchat": [
        {
            "patterns": [
                rf"https?://(www\.)?snapchat\.com/add/{PROFILE_ID}/?$",
                rf"https?://(www\.)?snapchat\.com/@{PROFILE_ID}/?$",
                rf"^@?{PROFILE_ID}$"
            ],
            "sanitized": "https://snapchat.com/@{id}"
        }
    ],
    "apple_music": [
        {
            "patterns": [
                rf"https?://(?:itunes|music)\.apple\.com/(?:[a-z]{{2}}/)?artist/(?:[A-Za-z0-9_\-\%\.]+/)?(?:id)?(?P<id>\d+)/?$",
                rf"https?://(?:itunes|music)\.apple\.com/(?:[a-z]{{2}}/)?artist/(?P<id>\d+)/?$",
                rf"^(?P<id>\d+)$"
            ],
            "sanitized": "https://music.apple.com/artist/{id}"
        }
    ],
    "bandcamp": [
        {
            "patterns": [
                rf"https?://{PROFILE_ID}\.bandcamp\.com/?$",
                rf"^{PROFILE_ID}$"
            ],
            "sanitized": "https://{id}.bandcamp.com"
        }
    ],
    "soundcloud": [
        {
            "patterns": [
                rf"https?://(www\.)?soundcloud\.com/{PROFILE_ID}/?$",
                rf"^{PROFILE_ID}$"
            ],
            "sanitized": "https://soundcloud.com/{id}"
        }
    ],
    "spotify": [
        {
            "patterns": [
                rf"https?://(open\.)?spotify\.com/artist/{PROFILE_ID}/?$",
                rf"^spotify:artist:{PROFILE_ID}$",
                rf"^{PROFILE_ID}$"
            ],
            "sanitized": "https://open.spotify.com/artist/{id}"
        },
        {
            "patterns": [
                rf"https?://(open\.)?spotify\.com/user/{PROFILE_ID}/?$"
            ],
            "sanitized": "https://open.spotify.com/user/{id}"
        }
    ],
    "stackoverflow": [
        {
            "patterns": [
                rf"https?://(www\.)?stackoverflow\.com/users/{PROFILE_ID}(/[A-Za-z0-9_\\-\\.]+)?/?$",
                rf"^{PROFILE_ID}$"
            ],
            "sanitized": "https://stackoverflow.com/users/{id}"
        }
    ],
    "steam": [
        {
            "patterns": [
                rf"https?://(www\.)?steamcommunity\.com/id/{PROFILE_ID}/?$",
                rf"^{PROFILE_ID}$"
            ],
            "sanitized": "https://steamcommunity.com/id/{id}"
        },
        {
            "patterns": [
                rf"https?://(www\.)?steamcommunity\.com/profiles/{PROFILE_ID}/?$"
            ],
            "sanitized": "https://steamcommunity.com/profiles/{id}"
        }
    ],
    "substack": [
        {
            "patterns": [
                rf"https?://{PROFILE_ID}\.substack\.com/?$",
                rf"https?://(www\.)?substack\.com/@{PROFILE_ID}/?$",
                rf"^{PROFILE_ID}$"
            ],
            "sanitized": "https://substack.com/@{id}"
        }
    ],
    "telegram": [
        {
            "patterns": [
                rf"https?://(www\.)?(t\.me|telegram\.me|telegram\.dog)/{PROFILE_ID_EXTENDED}/?$",
                rf"https?://(www\.)?web\.telegram\.org/[ak]/#@?{PROFILE_ID_EXTENDED}/?$",
                rf"^{PROFILE_ID_EXTENDED}$"
            ],
            "sanitized": "https://t.me/{id}"
        }
    ],
    "threads": [
        {
            "patterns": [
                rf"https?://(www\.)?threads\.net/@{PROFILE_ID}/?$",
                rf"^@?{PROFILE_ID}$"
            ],
            "sanitized": "https://threads.net/@{id}"
        }
    ],
    "tiktok": [
        {
            "patterns": [
                rf"https?://(www\.)?tiktok\.com/@{PROFILE_ID}/?$",
                rf"^@?{PROFILE_ID}$"
            ],
            "sanitized": "https://tiktok.com/@{id}"
        }
    ],
    "tumblr": [
        {
            "patterns": [
                rf"https?://{PROFILE_ID}\.tumblr\.com/?$",
                rf"https?://(www\.)?tumblr\.com/blog/{PROFILE_ID}/?$",
                rf"https?://(www\.)?tumblr\.com/{PROFILE_ID}/?$",
                rf"^{PROFILE_ID}$"
            ],
            "sanitized": "https://tumblr.com/{id}"
        }
    ],
    "twitch": [
        {
            "patterns": [
                rf"https?://(www\.)?twitch\.tv/{PROFILE_ID}/?$",
                rf"https?://m\.twitch\.tv/{PROFILE_ID}/?$",
                rf"^{PROFILE_ID}$"
            ],
            "sanitized": "https://twitch.tv/{id}"
        }
    ],
    "vk": [
        {
            "patterns": [
                rf"https?://(www\.)?vk\.com/{PROFILE_ID}/?$",
                rf"https?://m\.vk\.com/@?{PROFILE_ID}/?$",
                rf"^@?{PROFILE_ID}$"
            ],
            "sanitized": "https://vk.com/{id}"
        }
    ],
    "wechat": [
        {
            "patterns": [
                rf"https?://open\.weixin\.qq\.com/qr/code\?username={PROFILE_ID}$",
                rf"weixin://dl/chat\?{PROFILE_ID}$",
                rf"^{PROFILE_ID}$"
            ],
            "sanitized": "https://open.weixin.qq.com/qr/code?username={id}"
        }
    ],
    "weibo": [
        {
            "patterns": [
                rf"https?://(www\.)?weibo\.com/{PROFILE_ID}/?$",
                rf"^{PROFILE_ID}$"
            ],
            "sanitized": "https://weibo.com/{id}"
        },
        {
            "patterns": [
                rf"https?://(www\.)?weibo\.com/u/{PROFILE_ID}/?$"
            ],
            "sanitized": "https://weibo.com/u/{id}"
        }
    ],
    "vimeo": [
        {
            "patterns": [
                rf"https?://(www\.)?vimeo\.com/{PROFILE_ID}/?$",
                rf"^{PROFILE_ID}$"
            ],
            "sanitized": "https://vimeo.com/{id}"
        }
    ],
    "whatsapp": [
        {
            "patterns": [
                rf"https?://(www\.)?wa\.me/{PHONE_NUMBER}/?$",
                rf"https?://(www\.)?whatsapp\.com/send\?phone={PHONE_NUMBER}/?$",
                rf"^{PHONE_NUMBER}$"
            ],
            "sanitized": "https://wa.me/{id}"
        }
    ],
    "x": [
        {
            "patterns": [
                rf"https?://(www\.)?twitter\.com/@?{PROFILE_ID}/?$",
                rf"https?://mobile\.twitter\.com/@?{PROFILE_ID}/?$",
                rf"https?://x\.com/@?{PROFILE_ID}/?$",
                rf"^@?{PROFILE_ID}$"
            ],
            "sanitized": "https://x.com/{id}"
        }
    ],
    "youtube": [
        {
            "patterns": [
                rf"https?://(www\.)?youtube\.com/{PROFILE_ID_AT}/?$",
                rf"https?://(www\.)?youtube\.com/channel/{PROFILE_ID}/?$",
                rf"https?://(www\.)?youtube\.com/user/{PROFILE_ID}/?$",
                rf"https?://(www\.)?youtube\.com/c/{PROFILE_ID}/?$",
                rf"https?://m\.youtube\.com/c/{PROFILE_ID}/?$",
                rf"^{PROFILE_ID_AT}$"
            ],
            "sanitized": "https://youtube.com/{id}"
        }
    ],
    "producthunt": [
        {
            "patterns": [
                rf"https?://(www\.)?producthunt\.com/@{PROFILE_ID}/?$",
                rf"^@?{PROFILE_ID}$"
            ],
            "sanitized": "https://www.producthunt.com/@{id}"
        }
    ],
    "gumroad": [
        {
            "patterns": [
                rf"https?://{PROFILE_ID}\.gumroad\.com/?$",
                rf"https?://(www\.)?gumroad\.com/{PROFILE_ID}/?$",
                rf"^{PROFILE_ID}$"
            ],
            "sanitized": "https://gumroad.com/{id}"
        }
    ],
    "hashnode": [
        {
            "patterns": [
                rf"https?://(www\.)?hashnode\.com/@{PROFILE_ID}/?$",
                rf"https?://{PROFILE_ID}\.hashnode\.dev/?$",
                rf"^@?{PROFILE_ID}$"
            ],
            "sanitized": "https://hashnode.com/@{id}"
        }
    ]
}
