"""
data_loader.py
Loads the four mock data files (logs, metrics, deployments, alerts) and
optionally merges live GitHub data into the deployment list.
"""

import json
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _load_json(filename: str) -> List[Dict]:
    """Read a JSON file from the data directory. Returns [] on missing file."""
    path = DATA_DIR / filename
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _filter_by_service(records: List[Dict], service: Optional[str]) -> List[Dict]:
    if not service:
        return records
    service_lower = service.lower()
    return [r for r in records if r.get("service", "").lower() == service_lower]


# ---------------------------------------------------------------------------
# Public data loaders
# ---------------------------------------------------------------------------

def load_logs(service: Optional[str] = None) -> List[Dict]:
    return _filter_by_service(_load_json("logs.json"), service)


def load_metrics(service: Optional[str] = None) -> List[Dict]:
    return _filter_by_service(_load_json("metrics.json"), service)


def load_deployments(service: Optional[str] = None) -> List[Dict]:
    return _filter_by_service(_load_json("deployments.json"), service)


def load_alerts(service: Optional[str] = None) -> List[Dict]:
    return _filter_by_service(_load_json("alerts.json"), service)


# ---------------------------------------------------------------------------
# GitHub integration
# ---------------------------------------------------------------------------

async def load_github_data(owner: str, repo: str, per_page: int = 10) -> Dict[str, Any]:
    """Fetch GitHub data via the github_plugin. Returns {} on error."""
    try:
        from plugins.github_plugin import fetch as github_fetch  # noqa: PLC0415
        return await github_fetch({"owner": owner, "repo": repo, "per_page": per_page})
    except Exception as exc:
        return {"error": str(exc)}


def normalize_github_deployments(github_data: Dict[str, Any], service: str) -> List[Dict]:
    """
    Convert GitHub deployments + workflow_runs into the same shape as
    deployments.json entries so the correlation engine can treat them uniformly.
    """
    if not github_data or github_data.get("error"):
        return []

    normalized: List[Dict] = []

    # ── GitHub Deployments ───────────────────────────────────────────────────
    for dep in github_data.get("deployments") or []:
        if not isinstance(dep, dict) or dep.get("error"):
            continue
        normalized.append({
            "id": f"gh-dep-{dep.get('id', '')}",
            "service": service,
            "version": dep.get("ref", "unknown"),
            "environment": dep.get("environment", "production"),
            "status": dep.get("task", "deploy"),
            "timestamp": dep.get("created_at", ""),
            "triggered_by": (
                dep.get("creator", {}).get("login", "github")
                if isinstance(dep.get("creator"), dict)
                else "github"
            ),
            "source": "github_deployment",
            "html_url": f"https://github.com/{dep.get('creator', {}).get('login', '')}/{service}",
        })

    # ── GitHub Actions workflow runs ─────────────────────────────────────────
    for run in github_data.get("workflow_runs") or []:
        if not isinstance(run, dict) or run.get("error"):
            continue
        actor = run.get("triggering_actor") or {}
        normalized.append({
            "id": f"gh-run-{run.get('id', '')}",
            "service": service,
            "version": (run.get("head_sha") or "")[:8],
            "environment": "ci",
            "status": run.get("conclusion") or run.get("status", "unknown"),
            "timestamp": run.get("created_at", ""),
            "triggered_by": actor.get("login", "github-actions") if isinstance(actor, dict) else "github-actions",
            "workflow": run.get("name", ""),
            "branch": run.get("head_branch", ""),
            "source": "github_workflow",
            "html_url": run.get("html_url", ""),
        })

    return normalized
