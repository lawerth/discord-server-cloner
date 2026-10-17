import asyncio
from typing import Any, Callable, Dict, List, Optional

from src.api.client import DiscordClient
from src.api import endpoints


class GuildExtractor:
    def __init__(self, client: DiscordClient, guild_id: str | int):
        self.client = client
        self.guild_id = str(guild_id)

    async def extract_all(
        self,
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> Dict[str, Any]:
        if progress_callback:
            progress_callback("Fetching guild metadata", 0, 100)

        guild_data = await self.client.get_guild(self.guild_id)
        if not guild_data:
            raise ValueError(f"Could not fetch guild {self.guild_id}. Ensure account is a member.")

        overview = {
            "name": guild_data.get("name"),
            "description": guild_data.get("description"),
            "verification_level": guild_data.get("verification_level", 0),
            "default_message_notifications": guild_data.get("default_message_notifications", 0),
            "explicit_content_filter": guild_data.get("explicit_content_filter", 0),
            "afk_timeout": guild_data.get("afk_timeout", 300),
            "preferred_locale": guild_data.get("preferred_locale", "en-US"),
            "icon_url": endpoints.guild_icon_url(self.guild_id, guild_data["icon"]) if guild_data.get("icon") else None,
            "banner_url": endpoints.guild_banner_url(self.guild_id, guild_data["banner"]) if guild_data.get("banner") else None,
            "splash_url": endpoints.guild_splash_url(self.guild_id, guild_data["splash"]) if guild_data.get("splash") else None,
        }

        if progress_callback:
            progress_callback("Extracting roles", 20, 100)

        raw_roles = await self.client.get_guild_roles(self.guild_id)
        roles = []
        everyone_role = None

        raw_roles_sorted = sorted(raw_roles, key=lambda r: r.get("position", 0))

        for r in raw_roles_sorted:
            if str(r.get("id")) == str(self.guild_id):
                everyone_role = {
                    "id": str(r.get("id")),
                    "permissions": str(r.get("permissions", "0"))
                }
                continue

            if r.get("managed", False):
                continue

            role_info = {
                "id": str(r.get("id")),
                "name": r.get("name"),
                "color": r.get("color", 0),
                "hoist": r.get("hoist", False),
                "position": r.get("position", 1),
                "permissions": str(r.get("permissions", "0")),
                "mentionable": r.get("mentionable", False),
                "icon_url": endpoints.role_icon_url(r.get("id"), r["icon"]) if r.get("icon") else None
            }
            roles.append(role_info)

        if progress_callback:
            progress_callback("Extracting channels", 50, 100)

        raw_channels = await self.client.get_guild_channels(self.guild_id)
        categories = []
        channels = []

        for c in raw_channels:
            c_type = c.get("type", 0)
            c_data = {
                "id": str(c.get("id")),
                "name": c.get("name"),
                "type": c_type,
                "position": c.get("position", 0),
                "parent_id": str(c.get("parent_id")) if c.get("parent_id") else None,
                "topic": c.get("topic"),
                "nsfw": c.get("nsfw", False),
                "rate_limit_per_user": c.get("rate_limit_per_user", 0),
                "bitrate": c.get("bitrate", 64000) if c_type in [2, 13] else None,
                "user_limit": c.get("user_limit", 0) if c_type in [2, 13] else None,
                "permission_overwrites": c.get("permission_overwrites", [])
            }

            if c_type == 4:
                categories.append(c_data)
            else:
                channels.append(c_data)

        categories = sorted(categories, key=lambda x: x.get("position", 0))
        channels = sorted(channels, key=lambda x: x.get("position", 0))

        if progress_callback:
            progress_callback("Extracting emojis", 75, 100)

        raw_emojis = await self.client.get_guild_emojis(self.guild_id)
        emojis = []
        for e in raw_emojis:
            emojis.append({
                "id": str(e.get("id")),
                "name": e.get("name"),
                "animated": e.get("animated", False),
                "url": endpoints.emoji_url(e.get("id"), e.get("animated", False))
            })

        if progress_callback:
            progress_callback("Extracting stickers", 90, 100)

        raw_stickers = await self.client.get_guild_stickers(self.guild_id)
        stickers = []
        for s in raw_stickers:
            stickers.append({
                "id": str(s.get("id")),
                "name": s.get("name"),
                "description": s.get("description", ""),
                "tags": s.get("tags", "")
            })

        return {
            "source_guild_id": self.guild_id,
            "overview": overview,
            "everyone_role": everyone_role,
            "roles": roles,
            "categories": categories,
            "channels": channels,
            "emojis": emojis,
            "stickers": stickers
        }
