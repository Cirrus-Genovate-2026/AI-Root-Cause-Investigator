"""
github_plugin.py
Fetches incident-relevant GitHub data: commits, issues, workflow runs,
deployments, and releases.  Used by data_loader.py to enrich the
correlation engine with live repository signals.
"""

import asyncio
import os
from typing import Any, Dict

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Endpoints fetched in parallel for performance
_ENDPOINTS = {
    "commits":       "/commits?per_page={n}",
    "issues":        "/issues?state=open&per_page={n}",
    "workflows":     "/actions/workflows",
    "workflow_runs": "/actions/runs?per_page={n}",
    "deployments":   "/deployments?per_page={n}",
    "releases":      "/releases?per_page={n}",
}


async def fetch(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fetch a rich set of GitHub data for incident root-cause analysis.

    params:
      owner    (str, required) – GitHub org or user
      repo     (str, required) – repository name
      per_page (int, optional, default 10) – items per endpoint

    Returns a dict with keys:
      commits, issues, workflows, workflow_runs, deployments, releases
    Each value is a list or an {"error": "..."} dict on partial failure.
    """
    owner = params.get("owner")
    repo  = params.get("repo")
    if not owner or not repo:
        raise ValueError("Both 'owner' and 'repo' are required parameters.")

    per_page = int(params.get("per_page", 10))

    headers = {
        "Accept":               "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    try:
        import httpx
    except ImportError as exc:
        return {"error": f"httpx is not installed: {exc}"}

    base = f"https://api.github.com/repos/{owner}/{repo}"

    async def _get(name: str, url: str) -> tuple:
        try:
            r = await client.get(url, headers=headers)
            r.raise_for_status()
            return name, r.json()
        except httpx.HTTPStatusError as exc:
            return name, {"error": f"HTTP {exc.response.status_code}: {exc.response.text[:300]}"}
        except Exception as exc:
            return name, {"error": str(exc)}

    async with httpx.AsyncClient(timeout=30) as client:
        tasks = [
            _get(name, base + path.format(n=per_page))
            for name, path in _ENDPOINTS.items()
        ]
        results = await asyncio.gather(*tasks)

    data: Dict[str, Any] = dict(results)

    # Normalize: the workflow_runs endpoint wraps the list in a key
    wr = data.get("workflow_runs")
    if isinstance(wr, dict) and "workflow_runs" in wr:
        data["workflow_runs"] = wr["workflow_runs"]

    # Normalize: the workflows endpoint wraps the list in a key
    wf = data.get("workflows")
    if isinstance(wf, dict) and "workflows" in wf:
        data["workflows"] = wf["workflows"]

    return data
