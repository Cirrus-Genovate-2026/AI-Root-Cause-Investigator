"""
correlation_engine.py
Rule-based root cause analysis.  Each rule returns a "finding" dict that
describes the suspected cause, its severity and a confidence score (0–1).
Findings are sorted by confidence so the most likely cause comes first.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------
CPU_HIGH_PCT        = 80.0
MEMORY_HIGH_PCT     = 85.0
LATENCY_HIGH_MS     = 1000.0
ERROR_RATE_HIGH_PCT = 10.0
DEPLOY_WINDOW_MIN   = 30     # minutes before first alert = suspect deployment window


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_ts(ts: str) -> Optional[datetime]:
    if not ts:
        return None
    try:
        ts = ts.replace("Z", "+00:00")
        return datetime.fromisoformat(ts)
    except Exception:
        return None


def _incident_start(alerts: List[Dict]) -> Optional[datetime]:
    """Return the timestamp of the first critical/high alert."""
    severe = [a for a in alerts if a.get("severity", "").lower() in ("critical", "high", "error")]
    times = [_parse_ts(a.get("timestamp", "")) for a in severe]
    valid = [t for t in times if t]
    return min(valid) if valid else None


# ---------------------------------------------------------------------------
# Individual rules
# ---------------------------------------------------------------------------

def _rule_failed_deployment(deployments: List[Dict]) -> Optional[Dict]:
    failed = [
        d for d in deployments
        if str(d.get("status", "")).lower() in ("failure", "failed", "error")
    ]
    if not failed:
        return None
    versions = ", ".join(d.get("version", "?") for d in failed[:3])
    return {
        "rule":       "FAILED_DEPLOYMENT",
        "severity":   "critical",
        "summary":    f"Deployment failed: {versions}",
        "detail":     "One or more deployments/CI runs completed with a failure status.",
        "evidence":   failed[:3],
        "confidence": 0.95,
    }


def _rule_deployment_before_incident(
    deployments: List[Dict], incident_ts: Optional[datetime]
) -> Optional[Dict]:
    suspect = []
    for dep in deployments:
        dep_ts = _parse_ts(dep.get("timestamp", ""))
        if not dep_ts:
            continue
        if incident_ts:
            delta = (incident_ts - dep_ts).total_seconds() / 60
            if 0 <= delta <= DEPLOY_WINDOW_MIN:
                suspect.append(dep)
        else:
            # No clear incident time — include all recent deployments
            suspect.append(dep)
    if not suspect:
        return None
    top = suspect[0]
    return {
        "rule":       "DEPLOYMENT_BEFORE_INCIDENT",
        "severity":   "high",
        "summary":    f"Deployment '{top.get('version', '?')}' preceded the incident by ≤{DEPLOY_WINDOW_MIN} min",
        "detail":     top.get("notes", ""),
        "evidence":   suspect[:2],
        "confidence": 0.85,
    }


def _rule_github_ci_failure(deployments: List[Dict]) -> Optional[Dict]:
    gh_failures = [
        d for d in deployments
        if d.get("source") == "github_workflow"
        and str(d.get("status", "")).lower() in ("failure", "failed")
    ]
    if not gh_failures:
        return None
    names = ", ".join(d.get("workflow", "?") for d in gh_failures[:2])
    return {
        "rule":       "GITHUB_CI_FAILURE",
        "severity":   "high",
        "summary":    f"GitHub Actions workflow failed: {names}",
        "detail":     "CI pipeline failure may have allowed a broken build to reach production.",
        "evidence":   gh_failures[:2],
        "confidence": 0.90,
    }


def _rule_db_errors(logs: List[Dict]) -> Optional[Dict]:
    db_keywords = (
        "timeout", "connection refused", "connection pool",
        "database error", "db error", "deadlock", "pool exhausted",
        "payment_db", "postgres",
    )
    hits = [
        l for l in logs
        if any(kw in l.get("message", "").lower() for kw in db_keywords)
    ]
    if not hits:
        return None
    return {
        "rule":       "DATABASE_ERRORS",
        "severity":   "high",
        "summary":    f"Database errors in logs ({len(hits)} occurrences)",
        "detail":     hits[0].get("message", ""),
        "evidence":   hits[:3],
        "confidence": 0.82,
    }


def _rule_cpu_exhaustion(metrics: List[Dict]) -> Optional[Dict]:
    cpu_samples = [m for m in metrics if m.get("name") == "cpu_percent"]
    high = [m for m in cpu_samples if float(m.get("value", 0)) >= CPU_HIGH_PCT]
    if not high:
        return None
    peak = max(float(m.get("value", 0)) for m in high)
    return {
        "rule":       "CPU_EXHAUSTION",
        "severity":   "high",
        "summary":    f"CPU peaked at {peak:.0f}% (threshold {CPU_HIGH_PCT:.0f}%)",
        "detail":     "Resource contention likely caused cascading latency and timeouts.",
        "evidence":   high[-3:],
        "confidence": 0.75,
    }


def _rule_high_latency(metrics: List[Dict]) -> Optional[Dict]:
    lat_names = ("response_time_ms", "latency_ms", "p99_latency_ms")
    lat_samples = [m for m in metrics if m.get("name") in lat_names]
    high = [m for m in lat_samples if float(m.get("value", 0)) >= LATENCY_HIGH_MS]
    if not high:
        return None
    peak = max(float(m.get("value", 0)) for m in high)
    return {
        "rule":       "HIGH_LATENCY",
        "severity":   "high",
        "summary":    f"Response latency peaked at {peak:.0f} ms (SLO threshold {LATENCY_HIGH_MS:.0f} ms)",
        "detail":     "Downstream timeouts or resource blocking is slowing all requests.",
        "evidence":   high[-3:],
        "confidence": 0.72,
    }


def _rule_high_error_rate(metrics: List[Dict]) -> Optional[Dict]:
    err_names = ("error_rate_percent", "http_error_rate")
    err_samples = [m for m in metrics if m.get("name") in err_names]
    high = [m for m in err_samples if float(m.get("value", 0)) >= ERROR_RATE_HIGH_PCT]
    if not high:
        return None
    peak = max(float(m.get("value", 0)) for m in high)
    return {
        "rule":       "HIGH_ERROR_RATE",
        "severity":   "critical",
        "summary":    f"Error rate reached {peak:.1f}% (threshold {ERROR_RATE_HIGH_PCT:.0f}%)",
        "detail":     "SLO breach: majority of user requests are failing.",
        "evidence":   high[-3:],
        "confidence": 0.80,
    }


def _rule_memory_pressure(metrics: List[Dict]) -> Optional[Dict]:
    mem_names = ("memory_percent", "memory_usage_percent")
    mem_samples = [m for m in metrics if m.get("name") in mem_names]
    high = [m for m in mem_samples if float(m.get("value", 0)) >= MEMORY_HIGH_PCT]
    if not high:
        return None
    peak = max(float(m.get("value", 0)) for m in high)
    return {
        "rule":       "MEMORY_PRESSURE",
        "severity":   "medium",
        "summary":    f"Memory usage at {peak:.0f}% (threshold {MEMORY_HIGH_PCT:.0f}%)",
        "detail":     "Approaching OOM limit; GC pressure may cause latency spikes.",
        "evidence":   high[-2:],
        "confidence": 0.65,
    }


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run_rules(
    logs: List[Dict],
    metrics: List[Dict],
    deployments: List[Dict],
    alerts: List[Dict],
    service: str = "",
) -> List[Dict]:
    """
    Execute all rules and return a list of findings sorted by confidence
    (highest first).  Empty list means no anomalies detected.
    `service` is accepted for API consistency but rules operate on pre-filtered data.
    """
    _ = service  # reserved for future per-service threshold overrides
    incident_ts = _incident_start(alerts)

    rules_output = [
        _rule_failed_deployment(deployments),
        _rule_github_ci_failure(deployments),
        _rule_deployment_before_incident(deployments, incident_ts),
        _rule_db_errors(logs),
        _rule_high_error_rate(metrics),
        _rule_cpu_exhaustion(metrics),
        _rule_high_latency(metrics),
        _rule_memory_pressure(metrics),
    ]

    findings = [f for f in rules_output if f is not None]
    findings.sort(key=lambda f: f.get("confidence", 0), reverse=True)
    return findings
