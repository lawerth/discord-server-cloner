from datetime import datetime
import os
from pathlib import Path
from typing import Any, Dict, List

from src.utils.helpers import load_json, save_json

BACKUPS_DIR = Path("backups")


def create_backup(data: Dict[str, Any]) -> str:
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    server_name = data.get("overview", {}).get("name", "server")
    safe_name = "".join(c for c in server_name if c.isalnum() or c in (' ', '_', '-')).strip()
    safe_name = safe_name.replace(" ", "_") or "backup"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = BACKUPS_DIR / f"{safe_name}_{timestamp}.json"

    save_json(str(file_path), data)
    return str(file_path)


def list_backups() -> List[Dict[str, Any]]:
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    backups = []
    for file in sorted(BACKUPS_DIR.glob("*.json"), key=os.path.getmtime, reverse=True):
        content = load_json(str(file))
        if content and isinstance(content, dict) and "overview" in content:
            name = content.get("overview", {}).get("name", file.stem)
            mtime = datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            roles_count = len(content.get("roles", []))
            channels_count = len(content.get("channels", [])) + len(content.get("categories", []))
            emojis_count = len(content.get("emojis", []))

            backups.append({
                "path": str(file),
                "filename": file.name,
                "server_name": name,
                "date": mtime,
                "roles_count": roles_count,
                "channels_count": channels_count,
                "emojis_count": emojis_count,
                "data": content
            })
    return backups
