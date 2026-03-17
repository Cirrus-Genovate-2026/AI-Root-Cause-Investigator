import os
from typing import Any, Dict

POSTMAN_KEY = os.getenv("POSTMAN_API_KEY")


async def fetch(params: Dict[str, Any]):
    """Fetch Postman collections or workspaces. params: { type: 'collections'|'workspaces' }
    Requires POSTMAN_API_KEY in env.
    """
    if not POSTMAN_KEY:
        return {"error": "POSTMAN_API_KEY not set"}
    t = params.get("type", "collections")
    headers = {"X-Api-Key": POSTMAN_KEY}
    try:
        import httpx
    except Exception as e:
        return {"error": f"httpx not available or failed to import: {e}. Install a compatible httpx/httpcore version."}

    async with httpx.AsyncClient(timeout=30) as client:
        if t == "collections":
            url = "https://api.getpostman.com/collections"
        else:
            url = "https://api.getpostman.com/workspaces"
        try:
            r = await client.get(url, headers=headers)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            return {"error": str(e)}
