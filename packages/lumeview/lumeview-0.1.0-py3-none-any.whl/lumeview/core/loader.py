import json
import httpx
from typing import Any
from pathlib import Path

async def fetch_json_from_url(
    url: str, 
    method: str = "GET", 
    headers: dict = None, 
    data: Any = None,
    timeout: float = 120.0
) -> Any:
    """Fetches and validates JSON from a URL with full HTTP control."""
    async with httpx.AsyncClient(timeout=timeout) as client:
        # If data is provided, we'll try to send it as JSON if it's a dict/list
        # otherwise we send it as raw content.
        json_payload = None
        content = None
        
        if data:
            if isinstance(data, (dict, list)):
                json_payload = data
            else:
                content = str(data)

        response = await client.request(
            method=method,
            url=url,
            headers=headers,
            json=json_payload,
            content=content,
            follow_redirects=True
        )
        response.raise_for_status()
        return response.json()

def load_json_from_file(path: str) -> Any:
    """Loads and validates JSON from a local file."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)
