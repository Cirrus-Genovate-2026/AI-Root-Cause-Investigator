"""
evidence_builder.py
Packages raw findings + data into one structured evidence dict that is
passed both to the LLM and returned directly to the frontend.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _safe_sort_key(event: Dict) -> str:
    """Return the timestamp string, or empty string if absent."""
    return event.get("timestamp", "") or ""


def _build_timeline(
    deployments: List[Dict],
    alerts: List[Dict],
    logs: List[Dict],
) -> List[Dict]:
    """Merge deployments, alerts and error-level logs into a unified timeline."""
    events: List[Dict] = []

    for dep in deployments:
        status = str(dep.get("status", "")).lower()
        events.append({
            "type":        "deployment",
            "timestamp":   dep.get("timestamp", ""),
            "description": (
                f"[{dep.get('source', 'deploy').upper()}] "
                f"{dep.get('service', '')} → {dep.get('version', '?')} "
                f"({dep.get('environment', 'prod')}) — {dep.get('status', '?')}"
            ),
            "severity":    "critical" if status in ("failure", "failed", "error") else "info",
            "source":      dep.get("source", "deployment"),
            "meta":        dep,
        })

    for alert in alerts:
        events.append({
            "type":        "alert",
            "timestamp":   alert.get("timestamp", ""),
            "description": alert.get("message", alert.get("name", "Alert triggered")),
            "severity":    alert.get("severity", "warning"),
            "source":      "monitoring",
            "meta":        alert,
        })

    # Include only WARN / ERROR / CRITICAL log lines (noise filter)
    error_levels = {"error", "critical", "warn", "warning"}
    for log in logs:
        if log.get("level", "").lower() in error_levels:
            events.append({
                "type":        "log",
                "timestamp":   log.get("timestamp", ""),
                "description": f"[{log.get('host', '')}] {log.get('message', '')}",
                "severity":    "error" if log.get("level", "").lower() in ("error", "critical") else "warning",
                "source":      f"logs/{log.get('service', '')}",
                "meta":        log,
            })

    events.sort(key=_safe_sort_key)
    return events


def _summarise_metrics(metrics: List[Dict]) -> Dict[str, Dict]:
    """For each metric name, track peak value and sample count."""
    summary: Dict[str, Dict] = {}
    for m in metrics:
        name = m.get("name")
        raw_value = m.get("value")
        if not name or raw_value is None:
            continue
        value = float(raw_value)
        if name not in summary:
            summary[name] = {"peak": value, "latest": value, "samples": 1}
        else:
            summary[name]["samples"] += 1
            summary[name]["latest"] = value
            if value > summary[name]["peak"]:
                summary[name]["peak"] = value
    return summary


def _extract_github_insights(github_data: Optional[Dict]) -> Dict:
    """Pull the most relevant GitHub signals into a concise dict."""
    if not github_data or github_data.get("error"):
        return {}

    commits = [
        {
            "sha":     (c.get("sha") or "")[:8],
            "message": (c.get("commit", {}).get("message") or "").split("\n")[0][:120],
            "author":  c.get("commit", {}).get("author", {}).get("name", ""),
            "date":    c.get("commit", {}).get("author", {}).get("date", ""),
        }
        for c in (github_data.get("commits") or [])[:5]
        if isinstance(c, dict) and not c.get("error")
    ]

    issues = [
        {
            "number": i.get("number"),
            "title":  i.get("title", ""),
            "state":  i.get("state", ""),
            "url":    i.get("html_url", ""),
        }
        for i in (github_data.get("issues") or [])[:5]
        if isinstance(i, dict) and not i.get("error")
    ]

    failed_runs = [
        {
            "name":       r.get("name", ""),
            "branch":     r.get("head_branch", ""),
            "conclusion": r.get("conclusion", ""),
            "url":        r.get("html_url", ""),
        }
        for r in (github_data.get("workflow_runs") or [])[:10]
        if isinstance(r, dict) and str(r.get("conclusion", "")).lower() in ("failure", "failed")
    ]

    return {
        "recent_commits":      commits,
        "open_issues":         issues,
        "failed_workflow_runs": failed_runs,
        "total_workflow_runs": len(github_data.get("workflow_runs") or []),
    }


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def build_evidence(
    findings:    List[Dict],
    logs:        List[Dict],
    metrics:     List[Dict],
    deployments: List[Dict],
    alerts:      List[Dict],
    service:     str,
    github_data: Optional[Dict] = None,
) -> Dict[str, Any]:
    """
    Assemble the full evidence package returned by /analyze-incident.

    Returns a dict with:
      service, analyzed_at, root_cause, confidence, severity,
      findings, timeline, metrics_summary, github_insights, raw_counts
    """
    now_iso = datetime.now(timezone.utc).isoformat()

    primary = findings[0] if findings else None
    root_cause = primary["summary"] if primary else "Insufficient data to determine root cause"
    confidence = primary.get("confidence", 0.0) if primary else 0.0
    severity   = primary.get("severity", "info") if primary else "info"

    return {
        "service":         service,
        "analyzed_at":     now_iso,
        "root_cause":      root_cause,
        "confidence":      confidence,
        "severity":        severity,
        "findings":        findings,
        "timeline":        _build_timeline(deployments, alerts, logs),
        "metrics_summary": _summarise_metrics(metrics),
        "github_insights": _extract_github_insights(github_data),
        "raw_counts": {
            "logs":        len(logs),
            "metrics":     len(metrics),
            "deployments": len(deployments),
            "alerts":      len(alerts),
        },
    }
