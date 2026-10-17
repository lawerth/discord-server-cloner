import asyncio
from typing import Any, Callable, Dict, List, Optional

from src.api.client import DiscordClient
from src.utils.helpers import image_url_to_data_uri


class GuildBuilder:
    def __init__(self, client: DiscordClient, target_guild_id: str | int):
        self.client = client
        self.target_guild_id = str(target_guild_id)
        self.role_map: Dict[str, str] = {}
        self.category_map: Dict[str, str] = {}

    async def wipe_target(
        self,
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ):
        channels = await self.client.get_guild_channels(self.target_guild_id)
        for c in channels:
            try:
                await self.client.delete_channel(c["id"])
            except Exception:
                pass

        emojis = await self.client.get_guild_emojis(self.target_guild_id)
        for e in emojis:
            try:
                await self.client.delete_emoji(self.target_guild_id, e["id"])
            except Exception:
                pass

        roles = await self.client.get_guild_roles(self.target_guild_id)
        for r in roles:
            if str(r.get("id")) == str(self.target_guild_id) or r.get("managed", False):
                continue
            try:
                await self.client.delete_role(self.target_guild_id, r["id"])
            except Exception:
                pass

    def _remap_overwrites(self, overwrites: List[Dict[str, Any]], source_guild_id: str) -> List[Dict[str, Any]]:
        remapped = []
        for ow in overwrites:
            ow_type = ow.get("type", 0)
            target_id = str(ow.get("id"))

            if ow_type == 0:
                if target_id == str(source_guild_id):
                    target_id = str(self.target_guild_id)
                elif target_id in self.role_map:
                    target_id = self.role_map[target_id]
                else:
                    continue

            remapped.append({
                "id": target_id,
                "type": ow_type,
                "allow": str(ow.get("allow", "0")),
                "deny": str(ow.get("deny", "0"))
            })
        return remapped

    async def build(
        self,
        data: Dict[str, Any],
        options: Dict[str, bool],
        progress_callback: Optional[Callable[[str, str, int, int], None]] = None
    ):
        source_guild_id = str(data.get("source_guild_id", ""))
        self.role_map[source_guild_id] = str(self.target_guild_id)

        if options.get("server_settings", True):
            overview = data.get("overview", {})
            payload = {}
            if overview.get("name"):
                payload["name"] = overview["name"]
            if overview.get("description"):
                payload["description"] = overview["description"]
            if overview.get("verification_level") is not None:
                payload["verification_level"] = overview["verification_level"]
            if overview.get("default_message_notifications") is not None:
                payload["default_message_notifications"] = overview["default_message_notifications"]
            if overview.get("explicit_content_filter") is not None:
                payload["explicit_content_filter"] = overview["explicit_content_filter"]

            if overview.get("icon_url"):
                icon_data = await image_url_to_data_uri(self.client._http, overview["icon_url"])
                if icon_data:
                    payload["icon"] = icon_data

            if overview.get("banner_url"):
                banner_data = await image_url_to_data_uri(self.client._http, overview["banner_url"])
                if banner_data:
                    payload["banner"] = banner_data

            if payload:
                await self.client.modify_guild(self.target_guild_id, payload)

        if options.get("roles", True):
            everyone_role = data.get("everyone_role")
            if everyone_role and everyone_role.get("permissions"):
                try:
                    await self.client.modify_role(
                        self.target_guild_id,
                        self.target_guild_id,
                        {"permissions": str(everyone_role["permissions"])}
                    )
                except Exception:
                    pass

            roles = data.get("roles", [])
            total_roles = len(roles)

            roles_desc = sorted(roles, key=lambda r: r.get("position", 1), reverse=True)
            created_roles = []

            for idx, r in enumerate(roles_desc, 1):
                if progress_callback:
                    progress_callback("Roles", f"@{r['name']}", idx, total_roles)

                role_payload = {
                    "name": r.get("name"),
                    "color": r.get("color", 0),
                    "hoist": r.get("hoist", False),
                    "mentionable": r.get("mentionable", False),
                    "permissions": r.get("permissions", "0")
                }

                if r.get("icon_url"):
                    icon_uri = await image_url_to_data_uri(self.client._http, r["icon_url"])
                    if icon_uri:
                        role_payload["icon"] = icon_uri

                new_role = await self.client.create_role(self.target_guild_id, role_payload)
                if new_role and "id" in new_role:
                    new_id = str(new_role["id"])
                    self.role_map[str(r["id"])] = new_id
                    created_roles.append({
                        "id": new_id,
                        "position": r.get("position", 1)
                    })

            if created_roles:
                created_roles_sorted = sorted(created_roles, key=lambda x: x["position"])
                position_payload = [
                    {"id": cr["id"], "position": rank}
                    for rank, cr in enumerate(created_roles_sorted, start=1)
                ]
                try:
                    await self.client.update_role_positions(self.target_guild_id, position_payload)
                except Exception:
                    pass

        if options.get("channels", True):
            categories = data.get("categories", [])
            total_cats = len(categories)

            for idx, cat in enumerate(categories, 1):
                if progress_callback:
                    progress_callback("Categories", cat["name"], idx, total_cats)

                cat_payload = {
                    "name": cat["name"],
                    "type": 4,
                    "position": cat.get("position", 0),
                    "permission_overwrites": self._remap_overwrites(
                        cat.get("permission_overwrites", []),
                        source_guild_id
                    )
                }

                new_cat = await self.client.create_channel(self.target_guild_id, cat_payload)
                if new_cat and "id" in new_cat:
                    self.category_map[str(cat["id"])] = str(new_cat["id"])

            channels = data.get("channels", [])
            total_chans = len(channels)

            for idx, ch in enumerate(channels, 1):
                if progress_callback:
                    progress_callback("Channels", f"#{ch['name']}", idx, total_chans)

                target_parent_id = None
                if ch.get("parent_id") and str(ch["parent_id"]) in self.category_map:
                    target_parent_id = self.category_map[str(ch["parent_id"])]

                chan_payload = {
                    "name": ch["name"],
                    "type": ch.get("type", 0),
                    "position": ch.get("position", 0),
                    "parent_id": target_parent_id,
                    "topic": ch.get("topic"),
                    "nsfw": ch.get("nsfw", False),
                    "rate_limit_per_user": ch.get("rate_limit_per_user", 0),
                    "permission_overwrites": self._remap_overwrites(
                        ch.get("permission_overwrites", []),
                        source_guild_id
                    )
                }

                if ch.get("type") in [2, 13]:
                    if ch.get("bitrate"):
                        chan_payload["bitrate"] = ch["bitrate"]
                    if ch.get("user_limit"):
                        chan_payload["user_limit"] = ch["user_limit"]

                await self.client.create_channel(self.target_guild_id, chan_payload)

        if options.get("emojis", True):
            emojis = data.get("emojis", [])
            total_emojis = len(emojis)

            for idx, emo in enumerate(emojis, 1):
                if progress_callback:
                    progress_callback("Emojis", f":{emo['name']}:", idx, total_emojis)

                data_uri = await image_url_to_data_uri(self.client._http, emo["url"])
                if data_uri:
                    emoji_payload = {
                        "name": emo["name"],
                        "image": data_uri
                    }
                    await self.client.create_emoji(self.target_guild_id, emoji_payload)
