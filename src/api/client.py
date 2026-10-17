import asyncio
import random
from typing import Any, Dict, List, Optional
import httpx

from src.api import endpoints
from src.utils.spoof import get_default_headers

try:
    import h2
    HAS_HTTP2 = True
except ImportError:
    HAS_HTTP2 = False


class DiscordClient:
    def __init__(self, token: str, safe_mode: bool = True, locale: str = "en-US"):
        self.token = token.strip().replace("Bot ", "")
        self.safe_mode = safe_mode
        self.locale = locale
        self.headers = get_default_headers(self.token, locale=locale)
        self._http = httpx.AsyncClient(
            headers=self.headers,
            timeout=25.0,
            follow_redirects=True,
            http2=HAS_HTTP2
        )

    async def close(self):
        await self._http.aclose()

    async def _apply_delay(self):
        delay = random.uniform(0.6, 1.4) if self.safe_mode else random.uniform(0.18, 0.45)
        await asyncio.sleep(delay)

    async def request(
        self,
        method: str,
        url: str,
        apply_delay: bool = True,
        max_retries: int = 5,
        **kwargs
    ) -> httpx.Response:
        if apply_delay and method.upper() in ["POST", "PATCH", "DELETE", "PUT"]:
            await self._apply_delay()

        for attempt in range(max_retries):
            try:
                response = await self._http.request(method, url, **kwargs)

                if response.status_code == 429:
                    try:
                        retry_after = response.json().get("retry_after", 2.0)
                    except Exception:
                        retry_after = float(response.headers.get("Retry-After", 2.0))
                    
                    sleep_time = float(retry_after) + random.uniform(0.3, 0.8)
                    await asyncio.sleep(sleep_time)
                    continue

                return response
            except httpx.RequestError as e:
                if attempt == max_retries - 1:
                    raise e
                await asyncio.sleep(1.0 + attempt)

        return response

    async def get_me(self) -> Optional[Dict[str, Any]]:
        res = await self.request("GET", endpoints.USERS_ME, apply_delay=False)
        return res.json() if res.status_code == 200 else None

    async def get_guilds(self) -> List[Dict[str, Any]]:
        res = await self.request("GET", endpoints.USERS_ME_GUILDS, apply_delay=False)
        return res.json() if res.status_code == 200 else []

    async def get_guild(self, guild_id: str | int) -> Optional[Dict[str, Any]]:
        res = await self.request("GET", endpoints.guild_url(guild_id), apply_delay=False)
        return res.json() if res.status_code == 200 else None

    async def get_guild_channels(self, guild_id: str | int) -> List[Dict[str, Any]]:
        res = await self.request("GET", endpoints.guild_channels_url(guild_id), apply_delay=False)
        return res.json() if res.status_code == 200 else []

    async def get_guild_roles(self, guild_id: str | int) -> List[Dict[str, Any]]:
        res = await self.request("GET", endpoints.guild_roles_url(guild_id), apply_delay=False)
        return res.json() if res.status_code == 200 else []

    async def get_guild_emojis(self, guild_id: str | int) -> List[Dict[str, Any]]:
        res = await self.request("GET", endpoints.guild_emojis_url(guild_id), apply_delay=False)
        return res.json() if res.status_code == 200 else []

    async def get_guild_stickers(self, guild_id: str | int) -> List[Dict[str, Any]]:
        res = await self.request("GET", endpoints.guild_stickers_url(guild_id), apply_delay=False)
        return res.json() if res.status_code == 200 else []

    async def modify_guild(self, guild_id: str | int, payload: Dict[str, Any]) -> bool:
        res = await self.request("PATCH", endpoints.guild_url(guild_id), json=payload)
        return res.status_code in [200, 201]

    async def delete_channel(self, channel_id: str | int) -> bool:
        res = await self.request("DELETE", endpoints.channel_url(channel_id))
        return res.status_code in [200, 204]

    async def create_channel(self, guild_id: str | int, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        res = await self.request("POST", endpoints.guild_channels_url(guild_id), json=payload)
        return res.json() if res.status_code in [200, 201] else None

    async def delete_role(self, guild_id: str | int, role_id: str | int) -> bool:
        res = await self.request("DELETE", endpoints.guild_role_url(guild_id, role_id))
        return res.status_code in [200, 204]

    async def create_role(self, guild_id: str | int, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        res = await self.request("POST", endpoints.guild_roles_url(guild_id), json=payload)
        return res.json() if res.status_code in [200, 201] else None

    async def modify_role(self, guild_id: str | int, role_id: str | int, payload: Dict[str, Any]) -> bool:
        res = await self.request("PATCH", endpoints.guild_role_url(guild_id, role_id), json=payload)
        return res.status_code in [200, 201]

    async def update_role_positions(self, guild_id: str | int, positions: List[Dict[str, Any]]) -> bool:
        res = await self.request("PATCH", endpoints.guild_roles_url(guild_id), json=positions)
        return res.status_code in [200, 201]

    async def delete_emoji(self, guild_id: str | int, emoji_id: str | int) -> bool:
        res = await self.request("DELETE", endpoints.guild_emoji_url(guild_id, emoji_id))
        return res.status_code in [200, 204]

    async def create_emoji(self, guild_id: str | int, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        res = await self.request("POST", endpoints.guild_emojis_url(guild_id), json=payload)
        return res.json() if res.status_code in [200, 201] else None
