API_BASE = "https://discord.com/api/v9"
CDN_BASE = "https://cdn.discordapp.com"

# User endpoints
USERS_ME = f"{API_BASE}/users/@me"
USERS_ME_GUILDS = f"{API_BASE}/users/@me/guilds"

# Guild endpoints
def guild_url(guild_id: str | int) -> str:
    return f"{API_BASE}/guilds/{guild_id}"

def guild_channels_url(guild_id: str | int) -> str:
    return f"{API_BASE}/guilds/{guild_id}/channels"

def channel_url(channel_id: str | int) -> str:
    return f"{API_BASE}/channels/{channel_id}"

def guild_roles_url(guild_id: str | int) -> str:
    return f"{API_BASE}/guilds/{guild_id}/roles"

def guild_role_url(guild_id: str | int, role_id: str | int) -> str:
    return f"{API_BASE}/guilds/{guild_id}/roles/{role_id}"

def guild_emojis_url(guild_id: str | int) -> str:
    return f"{API_BASE}/guilds/{guild_id}/emojis"

def guild_emoji_url(guild_id: str | int, emoji_id: str | int) -> str:
    return f"{API_BASE}/guilds/{guild_id}/emojis/{emoji_id}"

def guild_stickers_url(guild_id: str | int) -> str:
    return f"{API_BASE}/guilds/{guild_id}/stickers"

def guild_sticker_url(guild_id: str | int, sticker_id: str | int) -> str:
    return f"{API_BASE}/guilds/{guild_id}/stickers/{sticker_id}"

# CDN Helpers
def guild_icon_url(guild_id: str | int, icon_hash: str) -> str:
    ext = "gif" if icon_hash.startswith("a_") else "png"
    return f"{CDN_BASE}/icons/{guild_id}/{icon_hash}.{ext}?size=1024"

def guild_banner_url(guild_id: str | int, banner_hash: str) -> str:
    ext = "gif" if banner_hash.startswith("a_") else "png"
    return f"{CDN_BASE}/banners/{guild_id}/{banner_hash}.{ext}?size=1024"

def guild_splash_url(guild_id: str | int, splash_hash: str) -> str:
    return f"{CDN_BASE}/splashes/{guild_id}/{splash_hash}.png?size=1024"

def emoji_url(emoji_id: str | int, animated: bool = False) -> str:
    ext = "gif" if animated else "png"
    return f"{CDN_BASE}/emojis/{emoji_id}.{ext}?size=128"

def role_icon_url(role_id: str | int, icon_hash: str) -> str:
    ext = "gif" if icon_hash.startswith("a_") else "png"
    return f"{CDN_BASE}/role-icons/{role_id}/{icon_hash}.{ext}?size=64"
