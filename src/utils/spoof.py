import base64
import json
from typing import Dict

DEFAULT_CLIENT_VERSION = "1.0.9160"
DEFAULT_BUILD_NUMBER = 329450
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) discord/1.0.9160 Chrome/128.0.6613.186 Electron/32.2.2 Safari/537.36"
)

def generate_super_properties(
    client_version: str = DEFAULT_CLIENT_VERSION,
    build_number: int = DEFAULT_BUILD_NUMBER,
    locale: str = "en-US"
) -> str:
    properties = {
        "os": "Windows",
        "browser": "Discord Client",
        "release_channel": "stable",
        "client_version": client_version,
        "os_version": "10.0.22631",
        "os_arch": "x64",
        "app_arch": "x64",
        "system_locale": locale,
        "browser_user_agent": DEFAULT_USER_AGENT,
        "browser_version": "32.2.2",
        "client_build_number": build_number,
        "native_build_number": None,
        "client_event_source": None
    }
    return base64.b64encode(json.dumps(properties).encode("utf-8")).decode("utf-8")


def get_default_headers(token: str, locale: str = "en-US") -> Dict[str, str]:
    clean_token = token.strip().replace("Bot ", "")
    return {
        "Authorization": clean_token,
        "Content-Type": "application/json",
        "User-Agent": DEFAULT_USER_AGENT,
        "X-Super-Properties": generate_super_properties(locale=locale),
        "X-Discord-Locale": locale,
        "X-Discord-Timezone": "UTC",
        "X-Debug-Options": "bugReporterEnabled",
        "Sec-Ch-Ua": '"Chromium";v="128", "Not;A=Brand";v="24"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Origin": "https://discord.com",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Accept-Language": "en-US,en;q=0.9",
    }
