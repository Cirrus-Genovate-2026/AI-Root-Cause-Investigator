"""
llm_summary.py
Sends structured evidence to an LLM (OpenAI or Azure OpenAI) and returns a
plain-English root-cause explanation.  Falls back to a rule-based summary
when no API key is configured so the demo always returns a useful result.
"""

import json
import os
from typing import Any, Dict, List

# ---------------------------------------------------------------------------
# Config from environment
# ---------------------------------------------------------------------------
_OPENAI_KEY            = os.getenv("OPENAI_API_KEY", "")
_OPENAI_MODEL          = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
_AZURE_ENDPOINT        = os.getenv("AZURE_OPENAI_ENDPOINT", "")
_AZURE_KEY             = os.getenv("AZURE_OPENAI_API_KEY", "")
_AZURE_DEPLOYMENT      = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")

_SYSTEM_PROMPT = (
    "You are a senior Site Reliability Engineer specializing in root cause analysis. "
    "Analyze the provided incident evidence and return a structured JSON explanation. "
    "Be concise, factual, and actionable. Do not guess beyond the evidence."
)


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

def _build_prompt(query: str, evidence: Dict[str, Any]) -> str:
    service   = evidence.get("service", "unknown")
    root_cause = evidence.get("root_cause", "")
    findings  = evidence.get("findings", [])
    timeline  = evidence.get("timeline", [])[-12:]   # last 12 events
    metrics   = evidence.get("metrics_summary", {})
    github    = evidence.get("github_insights", {})

    findings_txt = "\n".join(
        f"  [{f.get('severity','?').upper()}] {f.get('summary','')} — confidence {f.get('confidence',0):.0%}"
        for f in findings[:5]
    ) or "  None"

    timeline_txt = "\n".join(
        f"  {e.get('timestamp','')[:16]} | {e.get('type','?'):12} | {e.get('description','')[:110]}"
        for e in timeline
    ) or "  None"

    metrics_txt = "\n".join(
        f"  {k}: peak={v.get('peak')}, latest={v.get('latest')}, samples={v.get('samples')}"
        for k, v in list(metrics.items())[:6]
    ) or "  No metrics available"

    github_txt = ""
    if github:
        commits = github.get("recent_commits", [])
        issues  = github.get("open_issues", [])
        failed  = github.get("failed_workflow_runs", [])
        if commits:
            github_txt += "\nRecent GitHub Commits:\n" + "\n".join(
                f"  [{c.get('sha','')}] {c.get('message','')} — {c.get('author','')}"
                for c in commits[:4]
            )
        if failed:
            github_txt += "\nFailed GitHub Workflow Runs:\n" + "\n".join(
                f"  {r.get('name','')} on {r.get('branch','')} → {r.get('conclusion','')}"
                for r in failed[:3]
            )
        if issues:
            github_txt += "\nOpen GitHub Issues:\n" + "\n".join(
                f"  #{i.get('number','')} {i.get('title','')}"
                for i in issues[:3]
            )

    return f"""User Question: {query}

Service Under Investigation: {service}
Preliminary Rule-Based Assessment: {root_cause}

Key Evidence Findings (sorted by confidence):
{findings_txt}

Event Timeline (most recent events):
{timeline_txt}

Peak Metrics:
{metrics_txt}{github_txt}

---
Return ONLY valid JSON (no markdown fences) with this exact structure:
{{
  "root_cause": "<1-2 sentence summary>",
  "confidence_percent": <0-100>,
  "supporting_evidence": ["<bullet 1>", "<bullet 2>", ...],
  "next_steps": ["<action 1>", "<action 2>", ...],
  "prevention": ["<recommendation 1>", "<recommendation 2>", ...]
}}"""


# ---------------------------------------------------------------------------
# LLM callers
# ---------------------------------------------------------------------------

async def _call_openai(prompt: str) -> Dict[str, Any]:
    import openai
    client = openai.AsyncOpenAI(api_key=_OPENAI_KEY)
    response = await client.chat.completions.create(
        model=_OPENAI_MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user",   "content": prompt},
        ],
        max_tokens=900,
        response_format={"type": "json_object"},
    )
    text = response.choices[0].message.content.strip()
    return {"llm_response": json.loads(text), "provider": "openai"}


async def _call_azure_openai(prompt: str) -> Dict[str, Any]:
    from openai import AsyncAzureOpenAI
    client = AsyncAzureOpenAI(
        api_key=_AZURE_KEY,
        azure_endpoint=_AZURE_ENDPOINT,
        api_version="2024-02-01",
    )
    response = await client.chat.completions.create(
        model=_AZURE_DEPLOYMENT,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user",   "content": prompt},
        ],
        max_tokens=900,
        response_format={"type": "json_object"},
    )
    text = response.choices[0].message.content.strip()
    return {"llm_response": json.loads(text), "provider": "azure_openai"}


# ---------------------------------------------------------------------------
# Fallback: rule-based explanation (no LLM key required)
# ---------------------------------------------------------------------------

_NEXT_STEPS: Dict[str, List[str]] = {
    "FAILED_DEPLOYMENT":         ["Roll back to the last stable version immediately", "Review the deployment diff and CI logs for the breaking change", "Open a post-mortem ticket"],
    "GITHUB_CI_FAILURE":         ["Check the GitHub Actions workflow failure logs", "Fix the failing test/check and re-run the pipeline", "Enforce required status checks before merge"],
    "DEPLOYMENT_BEFORE_INCIDENT":["Compare the new deployment config against the previous version", "Perform a canary rollback if symptoms continue", "Review the PR #142 for breaking changes"],
    "DATABASE_ERRORS":           ["Check DB connection pool utilization and max-connections setting", "Review slow-query logs and connection timeout configs", "Restart the DB connection pool if safe to do so"],
    "HIGH_ERROR_RATE":           ["Enable circuit breaker on the failing downstream dependency", "Check error logs for the most common failure pattern", "Scale out replicas to reduce per-instance load"],
    "CPU_EXHAUSTION":            ["Scale out service replicas immediately", "Profile the application for CPU-intensive hot paths", "Set CPU auto-scaling policy to trigger at 60%"],
    "HIGH_LATENCY":              ["Verify downstream service health (payment-db, auth)", "Add or warm up a caching layer for hot queries", "Increase read replica count to distribute load"],
    "MEMORY_PRESSURE":           ["Increase pod memory limits by 20% as a short-term fix", "Profile for memory leaks using heap dump analysis", "Schedule GC tuning in the next working session"],
}

_PREVENTION: Dict[str, List[str]] = {
    "FAILED_DEPLOYMENT":         ["Add automated rollback gate triggered on high error rate", "Improve integration test coverage in CI"],
    "GITHUB_CI_FAILURE":         ["Add branch protection rules requiring CI to pass before merge", "Add pre-merge smoke tests against a staging environment"],
    "DEPLOYMENT_BEFORE_INCIDENT":["Implement canary deployments with automatic rollback", "Add post-deployment health-check gates in the pipeline"],
    "DATABASE_ERRORS":           ["Set connection pool monitoring alert at 70% utilization", "Add read replicas and connection pooler (e.g., PgBouncer)"],
    "HIGH_ERROR_RATE":           ["Define and enforce an SLO error budget alert at 5%", "Implement retry with exponential backoff on transient errors"],
    "CPU_EXHAUSTION":            ["Set HPA to scale at 60% CPU, not 80%", "Add CPU usage alert at 70% for early warning"],
    "HIGH_LATENCY":              ["Define p99 latency SLOs and alert on breach", "Add timeout + retry policies on all inter-service calls"],
    "MEMORY_PRESSURE":           ["Add memory alert at 75% for earlier response", "Run memory profiling in staging before every major release"],
}

_DEFAULT_STEPS       = ["Investigate logs for further details", "Check related services", "Page on-call team if not already done"]
_DEFAULT_PREVENTION  = ["Add comprehensive monitoring and alerting", "Document a runbook for this incident scenario"]


def _fallback(evidence: Dict[str, Any]) -> Dict[str, Any]:
    findings = evidence.get("findings", [])
    if not findings:
        return {
            "llm_response": {
                "root_cause":          "Insufficient data to determine root cause. Set up an LLM API key for deeper analysis.",
                "confidence_percent":  0,
                "supporting_evidence": [],
                "next_steps":          ["Check logs manually", "Review recent deployments in GitHub"],
                "prevention":          ["Configure OPENAI_API_KEY or AZURE_OPENAI_API_KEY for AI-powered analysis"],
            },
            "provider": "fallback",
        }

    top    = findings[0]
    rule   = top.get("rule", "")
    others = [f.get("summary", "") for f in findings[1:4]]

    return {
        "llm_response": {
            "root_cause":          top.get("summary", "Unknown cause"),
            "confidence_percent":  int(top.get("confidence", 0) * 100),
            "supporting_evidence": [top.get("detail", "")] + others,
            "next_steps":          _NEXT_STEPS.get(rule, _DEFAULT_STEPS),
            "prevention":          _PREVENTION.get(rule, _DEFAULT_PREVENTION),
        },
        "provider": "fallback",
    }


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

async def get_llm_explanation(query: str, evidence: Dict[str, Any]) -> Dict[str, Any]:
    """
    Try OpenAI → Azure OpenAI → rule-based fallback.
    Always returns a dict with keys: llm_response, provider.
    """
    prompt = _build_prompt(query, evidence)

    if _OPENAI_KEY:
        try:
            return await _call_openai(prompt)
        except Exception:
            pass  # fall through

    if _AZURE_KEY and _AZURE_ENDPOINT:
        try:
            return await _call_azure_openai(prompt)
        except Exception:
            pass  # fall through

    return _fallback(evidence)
