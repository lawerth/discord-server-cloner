import asyncio
import os
import sys
import time
from rich.console import Console

from src.api.client import DiscordClient
from src.core.backup import create_backup, list_backups
from src.core.builder import GuildBuilder
from src.core.extractor import GuildExtractor
from src.ui.banner import print_banner
from src.ui.dashboard import CloneDashboard, show_summary
from src.ui.prompts import (
    prompt_clone_options,
    prompt_confirm,
    prompt_main_menu,
    prompt_select_backup,
    prompt_select_guild,
    prompt_speed_mode,
    prompt_token,
)

console = Console()


async def run_live_clone(client: DiscordClient, guilds: list):
    print_banner()

    source_guild_id = await prompt_select_guild(guilds, "Select source server:")
    target_guild_id = await prompt_select_guild(guilds, "Select target server:")

    if source_guild_id == target_guild_id:
        console.print("[red]Source and target server cannot be the same.[/]")
        time.sleep(1.5)
        return

    source_name = next((g["name"] for g in guilds if str(g["id"]) == source_guild_id), source_guild_id)
    target_name = next((g["name"] for g in guilds if str(g["id"]) == target_guild_id), target_guild_id)

    print_banner()
    console.print(f"[dim]Source:[/] [cyan]{source_name}[/] -> [dim]Target:[/] [magenta]{target_name}[/]\n")

    options = await prompt_clone_options()
    safe_mode = await prompt_speed_mode()
    client.safe_mode = safe_mode

    if not await prompt_confirm(f"Clone '{source_name}' into '{target_name}'?"):
        console.print("[yellow]Cancelled.[/]")
        time.sleep(1)
        return

    start_time = time.time()

    with console.status("[cyan]Extracting source server structure...", spinner="dots"):
        extractor = GuildExtractor(client, source_guild_id)
        extracted_data = await extractor.extract_all()

    backup_path = create_backup(extracted_data)
    console.print(f"[dim]Saved local backup to {backup_path}[/]")

    builder = GuildBuilder(client, target_guild_id)

    if options.get("wipe_target", True):
        with console.status("[yellow]Wiping target server channels, roles and emojis...", spinner="dots"):
            await builder.wipe_target()
        console.print("[green]Target server wiped.[/]")

    roles_list = extracted_data.get("roles", []) if options.get("roles") else []
    cats_list = extracted_data.get("categories", []) if options.get("channels") else []
    chans_list = extracted_data.get("channels", []) if options.get("channels") else []
    emojis_list = extracted_data.get("emojis", []) if options.get("emojis") else []

    with CloneDashboard() as dashboard:
        if roles_list:
            dashboard.add_task("Roles", total=len(roles_list))
        if cats_list:
            dashboard.add_task("Categories", total=len(cats_list))
        if chans_list:
            dashboard.add_task("Channels", total=len(chans_list))
        if emojis_list:
            dashboard.add_task("Emojis", total=len(emojis_list))

        def on_progress(category_name: str, item_name: str, idx: int, total: int):
            dashboard.update_task(category_name, advance=1, description=item_name)

        await builder.build(extracted_data, options, progress_callback=on_progress)

    elapsed = time.time() - start_time
    show_summary(
        source_name=source_name,
        target_name=target_name,
        roles_count=len(roles_list),
        channels_count=len(cats_list) + len(chans_list),
        emojis_count=len(emojis_list),
        elapsed_time=elapsed,
        backup_file=backup_path
    )
    await prompt_confirm("Press Enter to return.")


async def run_backup_server(client: DiscordClient, guilds: list):
    print_banner()
    source_guild_id = await prompt_select_guild(guilds, "Select server to backup:")
    source_name = next((g["name"] for g in guilds if str(g["id"]) == source_guild_id), source_guild_id)

    with console.status(f"[cyan]Extracting '{source_name}'...", spinner="dots"):
        extractor = GuildExtractor(client, source_guild_id)
        data = await extractor.extract_all()
        backup_path = create_backup(data)

    console.print(f"\n[green]Backup saved to:[/] [cyan]{backup_path}[/]\n")
    await prompt_confirm("Press Enter to return.")


async def run_restore_backup(client: DiscordClient, guilds: list):
    print_banner()
    backups = list_backups()
    if not backups:
        console.print("[red]No backup files found in 'backups/' directory.[/]")
        time.sleep(1.5)
        return

    selected_backup = await prompt_select_backup(backups)
    if not selected_backup:
        return

    target_guild_id = await prompt_select_guild(guilds, "Select target server:")
    target_name = next((g["name"] for g in guilds if str(g["id"]) == target_guild_id), target_guild_id)

    options = await prompt_clone_options()
    safe_mode = await prompt_speed_mode()
    client.safe_mode = safe_mode

    if not await prompt_confirm(f"Restore '{selected_backup['server_name']}' into '{target_name}'?"):
        return

    start_time = time.time()
    builder = GuildBuilder(client, target_guild_id)

    if options.get("wipe_target", True):
        with console.status("[yellow]Wiping target server...", spinner="dots"):
            await builder.wipe_target()
        console.print("[green]Target server wiped.[/]")

    extracted_data = selected_backup["data"]
    roles_list = extracted_data.get("roles", []) if options.get("roles") else []
    cats_list = extracted_data.get("categories", []) if options.get("channels") else []
    chans_list = extracted_data.get("channels", []) if options.get("channels") else []
    emojis_list = extracted_data.get("emojis", []) if options.get("emojis") else []

    with CloneDashboard() as dashboard:
        if roles_list:
            dashboard.add_task("Roles", total=len(roles_list))
        if cats_list:
            dashboard.add_task("Categories", total=len(cats_list))
        if chans_list:
            dashboard.add_task("Channels", total=len(chans_list))
        if emojis_list:
            dashboard.add_task("Emojis", total=len(emojis_list))

        def on_progress(category_name: str, item_name: str, idx: int, total: int):
            dashboard.update_task(category_name, advance=1, description=item_name)

        await builder.build(extracted_data, options, progress_callback=on_progress)

    elapsed = time.time() - start_time
    show_summary(
        source_name=f"[Backup] {selected_backup['server_name']}",
        target_name=target_name,
        roles_count=len(roles_list),
        channels_count=len(cats_list) + len(chans_list),
        emojis_count=len(emojis_list),
        elapsed_time=elapsed,
        backup_file=selected_backup["path"]
    )
    await prompt_confirm("Press Enter to return.")


async def run_wipe_server(client: DiscordClient, guilds: list):
    print_banner()
    target_guild_id = await prompt_select_guild(guilds, "Select server to wipe:")
    target_name = next((g["name"] for g in guilds if str(g["id"]) == target_guild_id), target_guild_id)

    console.print(f"\n[bold red]WARNING:[/] All channels, roles, and emojis in '{target_name}' will be deleted.")
    if not await prompt_confirm(f"Are you sure you want to wipe '{target_name}'?"):
        console.print("[yellow]Cancelled.[/]")
        time.sleep(1)
        return

    with console.status("[yellow]Wiping server...", spinner="dots"):
        builder = GuildBuilder(client, target_guild_id)
        await builder.wipe_target()

    console.print(f"\n[green]'{target_name}' wiped successfully.[/]\n")
    await prompt_confirm("Press Enter to return.")


async def main_async():
    print_banner()

    while True:
        token = await prompt_token()
        with console.status("[cyan]Verifying token...", spinner="dots"):
            client = DiscordClient(token)
            user_data = await client.get_me()

        if user_data:
            username = user_data.get("username", "User")
            user_id = user_data.get("id")
            console.print(f"[green]Authenticated as[/] [bold white]{username}[/] [dim]({user_id})[/]\n")
            time.sleep(1)
            break
        else:
            console.print("[red]Invalid token. Try again.[/]\n")
            await client.close()

    with console.status("[cyan]Fetching servers...", spinner="dots"):
        guilds = await client.get_guilds()

    if not guilds:
        console.print("[red]No accessible servers found for this account.[/]")
        await client.close()
        return

    try:
        while True:
            print_banner()
            choice = await prompt_main_menu()

            if choice == "clone_live":
                await run_live_clone(client, guilds)
            elif choice == "backup_server":
                await run_backup_server(client, guilds)
            elif choice == "restore_backup":
                await run_restore_backup(client, guilds)
            elif choice == "wipe_server":
                await run_wipe_server(client, guilds)
            elif choice == "exit":
                break
    finally:
        await client.close()


def main():
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(0)


if __name__ == "__main__":
    main()
