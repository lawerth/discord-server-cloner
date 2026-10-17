import base64
import json
from pathlib import Path
from typing import Any, Optional
import httpx

async def image_url_to_data_uri(client: httpx.AsyncClient, url: Optional[str]) -> Optional[str]:
    if not url:
        return None
    try:
        resp = await client.get(url, timeout=15.0)
        if resp.status_code == 200:
            content_type = resp.headers.get("content-type", "image/png").split(";")[0].strip()
            if not content_type.startswith("image/"):
                content_type = "image/png"
            b64_data = base64.b64encode(resp.content).decode("utf-8")
            return f"data:{content_type};base64,{b64_data}"
    except Exception:
        pass
    return None


def save_json(file_path: str, data: Any) -> bool:
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def load_json(file_path: str) -> Optional[Any]:
    try:
        path = Path(file_path)
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None
