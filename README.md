# discord-server-cloner

A high-performance Discord server cloning and backup utility designed to replicate server architecture, role hierarchies, permission overwrites, channels (including restricted/staff channels), and emojis.

---

## Features

- **Channel Extraction without Elevated Permissions:** Reads the raw channel metadata payload from Discord's client API. Unlike bot tokens (which are filtered server-side if `VIEW_CHANNEL` is denied), user client endpoints receive the full channel hierarchy, allowing extraction of restricted and hidden channels.
- **Permission Overwrites Resolver:** Maps role IDs from the source guild to the newly generated role IDs on the target guild, ensuring private channels retain identical permission boundaries.
- **Full Architecture Replication:**
  - Roles: name, color, position, hoist, mentionable, role icons, and exact permission bitfield.
  - Categories & Channels: Text, Voice, Announcement, Stage, and Forum channels with topic, NSFW, slowmode, bitrate, and user limits.
  - Custom Emojis: downloads static and animated emojis from source and re-uploads them.
  - Server Settings: server name, icon, banner, splash, verification level, and notification settings.
- **Offline Backups (`.json`):** Export complete server structures to structured JSON files and restore them to any guild at any time.
- **Target Server Cleaner:** Optional pre-clone wipe to delete existing channels, roles, and emojis on the destination guild.
- **Rate-Limit & Anti-Detection Safeguards:** Mimics official Discord client headers (`User-Agent`, `X-Super-Properties`), implements randomized human jitter between requests, and handles HTTP 429 rate limits with exponential backoff.

---

## Prerequisites

- Python 3.10 or higher
- A Discord user account with administrative permissions on the **target** server (you only need regular membership on the **source** server).

---

## Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/your-username/discord-server-cloner.git
cd discord-server-cloner
pip install -r requirements.txt
```

Windows users can also launch directly via `run.bat`.

---

## Usage

Start the interactive CLI:

```bash
python main.py
```

### Workflow

1. **Authentication:** Enter your Discord account token when prompted.
2. **Action Selection:**
   - `Clone server (direct)`: Clone directly from one guild to another.
   - `Create backup (.json)`: Export a guild schema to the `backups/` directory.
   - `Restore from backup`: Build a guild using a saved JSON backup file.
   - `Wipe target server`: Clear all channels, roles, and emojis on a server.
3. **Configuration:**
   - Select the source and target guilds using the arrow keys.
   - Choose which components to replicate (roles, channels, emojis, server settings).
   - Select speed mode (`Safe` with randomized jitter vs. `Fast`).

---

## Technical Details

### Why User Tokens (Selfbot API)?

Discord enforces permission checks differently depending on the authorization type:

| Authorization | Permission Handling | Hidden/Restricted Channel Visibility |
| :--- | :--- | :--- |
| `Bot <token>` | **Server-Side Filtered** | Denied. Channels without `VIEW_CHANNEL` are stripped from the response by the server. |
| `<user_token>` | **Client-Side Evaluated** | Allowed. The REST endpoint (`/api/v9/guilds/{id}/channels`) returns the complete channel tree so the desktop client can cache it and manage layout state locally. |

This tool leverages the user client endpoint to parse the complete channel layout and rebuild it on the destination server.

---

## Disclaimer

This software is provided for educational and backup purposes only. Automating user accounts (self-botting) violates Discord's Terms of Service. Use this tool at your own risk. The author is not responsible for any account suspensions or actions taken by Discord.

---

## License

Distributed under the [MIT License](LICENSE).
