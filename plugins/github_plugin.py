import os
import asyncio
from typing import Any, Dict

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


async def fetch(params: Dict[str, Any]):
    """Fetch a rich set of GitHub data for a repo.
    params: { owner: str, repo: str, per_page: int }
    Returns dict with commits, issues, workflows, workflow_runs, deployments, releases.
    """
    owner = params.get("owner")
    repo = params.get("repo")
    if not owner or not repo:
        raise ValueError("owner and repo required")
    per_page = int(params.get("per_page", 10))

    headers = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    try:
        import httpx
    except Exception as e:
        return {"error": f"httpx not available or failed to import: {e}. Install a compatible httpx/httpcore version."}

    base = f"https://api.github.com/repos/{owner}/{repo}"
    async with httpx.AsyncClient(timeout=30) as client:
        # prepare endpoint list
        endpoints = {
            "commits": f"{base}/commits?per_page={per_page}",
            "issues": f"{base}/issues?per_page={per_page}",
            "workflows": f"{base}/actions/workflows",
            "workflow_runs": f"{base}/actions/runs?per_page={per_page}",
            "deployments": f"{base}/deployments?per_page={per_page}",
            "releases": f"{base}/releases?per_page={per_page}",
        }

        async def fetch_url(name, url):
            try:
                r = await client.get(url, headers=headers)
                r.raise_for_status()
                return name, r.json()
            except httpx.HTTPStatusError as e:
                return name, {"error": f"HTTP {e.response.status_code}: {e.response.text[:200]}"}
            except Exception as e:
                return name, {"error": str(e)}

        tasks = [fetch_url(n, u) for n, u in endpoints.items()]
        results = await asyncio.gather(*tasks, return_exceptions=False)
        data = {k: v for k, v in results}

        # normalize workflow_runs list if present
        if isinstance(data.get("workflow_runs"), dict) and data["workflow_runs"].get("workflow_runs"):
            data["workflow_runs"] = data["workflow_runs"]["workflow_runs"]

        return data
