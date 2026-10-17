from typing import Any, Dict, List, Optional
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator

async def prompt_token() -> str:
    result = await inquirer.secret(
        message="Discord token:",
        transformer=lambda _: "[entered]",
        validate=lambda val: len(val.strip()) > 20 or "Token appears invalid.",
        invalid_message="Token is too short."
    ).execute_async()
    return result.strip()


async def prompt_main_menu() -> str:
    return await inquirer.select(
        message="Select action:",
        choices=[
            Choice(value="clone_live", name="1. Clone server (direct)"),
            Choice(value="backup_server", name="2. Export backup to JSON"),
            Choice(value="restore_backup", name="3. Restore server from JSON"),
            Choice(value="wipe_server", name="4. Wipe server"),
            Separator(),
            Choice(value="exit", name="5. Exit")
        ]
    ).execute_async()


async def prompt_select_guild(guilds: List[Dict[str, Any]], title: str) -> str:
    choices = [
        Choice(
            value=str(g["id"]),
            name=f"{g.get('name', 'Unknown')} ({g['id']})"
        )
        for g in guilds
    ]
    return await inquirer.select(
        message=title,
        choices=choices,
        qmark=">"
    ).execute_async()


async def prompt_clone_options() -> Dict[str, bool]:
    selected = await inquirer.checkbox(
        message="Select components to clone (Space to toggle, Enter to confirm):",
        choices=[
            Choice("roles", name="Roles and hierarchy", enabled=True),
            Choice("channels", name="Channels and categories (including restricted)", enabled=True),
            Choice("emojis", name="Custom emojis", enabled=True),
            Choice("server_settings", name="Server name, icon and banner", enabled=True),
            Choice("wipe_target", name="Wipe target server before building", enabled=True)
        ]
    ).execute_async()

    return {
        "roles": "roles" in selected,
        "channels": "channels" in selected,
        "emojis": "emojis" in selected,
        "server_settings": "server_settings" in selected,
        "wipe_target": "wipe_target" in selected
    }


async def prompt_speed_mode() -> bool:
    return await inquirer.select(
        message="Execution mode:",
        choices=[
            Choice(value=True, name="Safe mode (randomized jitter, handles rate limits)"),
            Choice(value=False, name="Fast mode (minimal delays)")
        ]
    ).execute_async()


async def prompt_confirm(message: str) -> bool:
    return await inquirer.confirm(message=message, default=True).execute_async()


async def prompt_select_backup(backups: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not backups:
        return None
    choices = [
        Choice(
            value=b,
            name=f"{b['server_name']} | {b['date']} | {b['roles_count']} roles, {b['channels_count']} channels"
        )
        for b in backups
    ]
    return await inquirer.select(
        message="Select backup file:",
        choices=choices
    ).execute_async()
