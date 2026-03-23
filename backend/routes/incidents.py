"""
incidents.py — API route handlers
Endpoints:
  GET  /api/v1/health
  POST /api/v1/analyze-incident
  GET  /api/v1/timeline
"""

from typing import Annotated, Any, Dict, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

from backend.services.data_loader import (
    load_alerts,
    load_deployments,
    load_github_data,
    load_logs,
    load_metrics,
    normalize_github_deployments,
)
from backend.services.correlation_engine import run_rules
from backend.services.evidence_builder import build_evidence
from backend.services.llm_summary import get_llm_explanation
from backend.services.parser import parse_query

router = APIRouter()


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class AnalyzeRequest(BaseModel):
    query:        str
    service:      Optional[str] = None
    github_owner: Optional[str] = None
    github_repo:  Optional[str] = None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok", "version": "1.0.0"}


@router.post("/analyze-incident")
async def analyze_incident(req: AnalyzeRequest) -> Dict[str, Any]:
    """
    Full incident root-cause analysis pipeline:
      parse → load data → merge GitHub → correlate → build evidence → LLM
    """
    # 1. Parse the natural-language query
    parsed  = parse_query(req.query)
    service = req.service or parsed["service"]

    # 2. Load mock data
    logs        = load_logs(service)
    metrics     = load_metrics(service)
    deployments = load_deployments(service)
    alerts      = load_alerts(service)

    # 3. Optionally layer in live GitHub data
    github_data: Dict[str, Any] = {}
    if req.github_owner and req.github_repo:
        github_data  = await load_github_data(req.github_owner, req.github_repo)
        gh_deps      = normalize_github_deployments(github_data, service)
        deployments  = gh_deps + deployments   # GitHub evidence takes priority

    # 4. Run rule-based correlation
    findings = run_rules(logs, metrics, deployments, alerts, service)

    # 5. Build structured evidence package
    evidence = build_evidence(
        findings, logs, metrics, deployments, alerts, service, github_data
    )

    # 6. Get LLM (or fallback) explanation
    explanation = await get_llm_explanation(req.query, evidence)

    return {
        "query":       req.query,
        "parsed":      parsed,
        "evidence":    evidence,
        "explanation": explanation,
    }


@router.get("/timeline")
async def get_timeline(
    service:      Annotated[str,           Query(description="Service name to query")] = "checkout",
    github_owner: Annotated[Optional[str], Query(description="GitHub org or user")] = None,
    github_repo:  Annotated[Optional[str], Query(description="GitHub repository name")] = None,
) -> Dict[str, Any]:
    """Return a merged chronological event timeline for the given service."""
    deployments = load_deployments(service)
    alerts      = load_alerts(service)
    logs        = [
        l for l in load_logs(service)
        if l.get("level", "").lower() in ("error", "critical", "warn", "warning")
    ]

    github_data: Dict[str, Any] = {}
    if github_owner and github_repo:
        github_data  = await load_github_data(github_owner, github_repo)
        gh_deps      = normalize_github_deployments(github_data, service)
        deployments  = gh_deps + deployments

    events = []
    for dep in deployments:
        events.append({"type": "deployment", "timestamp": dep.get("timestamp", ""), "data": dep})
    for alert in alerts:
        events.append({"type": "alert",      "timestamp": alert.get("timestamp", ""), "data": alert})
    for log in logs[:30]:
        events.append({"type": "log",        "timestamp": log.get("timestamp", ""),  "data": log})

    events.sort(key=lambda e: e.get("timestamp", ""))

    return {"service": service, "total": len(events), "events": events}
