"""
parser.py
Extracts service name and time range from a natural-language user query.
No heavy NLP — keyword matching is sufficient for the demo.
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Tuple

# ---------------------------------------------------------------------------
# Service keyword map  ──  keyword  →  canonical service name
# ---------------------------------------------------------------------------
_SERVICE_KEYWORDS: Dict[str, str] = {
    # checkout
    "checkout": "checkout",
    "cart":     "checkout",
    "order":    "checkout",
    "purchase": "checkout",
    # payment
    "payment":  "payment",
    "pay":      "payment",
    "billing":  "payment",
    "invoice":  "payment",
    "stripe":   "payment",
    # auth
    "auth":     "auth",
    "login":    "auth",
    "token":    "auth",
    "session":  "auth",
    "jwt":      "auth",
    "sso":      "auth",
    # api-gateway
    "gateway":      "api-gateway",
    "api-gateway":  "api-gateway",
    "proxy":        "api-gateway",
    # notification
    "notification": "notification",
    "email":        "notification",
    "sms":          "notification",
    # inventory
    "inventory": "inventory",
    "stock":     "inventory",
    "warehouse": "inventory",
    # database (if queried directly)
    "database": "database",
    "postgres": "database",
    "mysql":    "database",
    "mongo":    "database",
}


def extract_service(query: str) -> Optional[str]:
    """Return the canonical service name found in the query, or None."""
    q = query.lower()
    # Longer keywords first to avoid partial-match false positives
    for kw in sorted(_SERVICE_KEYWORDS, key=len, reverse=True):
        if kw in q:
            return _SERVICE_KEYWORDS[kw]
    return None


def extract_time_range(query: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Return (start_iso, end_iso) UTC strings derived from time hints in the
    query, or (None, None) if no hint is found.
    """
    q = query.lower()
    now = datetime.now(timezone.utc)

    if "last hour" in q:
        return (now - timedelta(hours=1)).isoformat(), now.isoformat()

    if "last 24 hours" in q or "last day" in q:
        return (now - timedelta(days=1)).isoformat(), now.isoformat()

    if "yesterday" in q or "last night" in q:
        yesterday = (now - timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end_of_yesterday = yesterday.replace(hour=23, minute=59, second=59)
        return yesterday.isoformat(), end_of_yesterday.isoformat()

    if "today" in q or "this morning" in q:
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return start.isoformat(), now.isoformat()

    return None, None


def parse_query(query: str) -> Dict:
    """
    Parse a free-text user query and return a structured dict with:
      - original:   the raw query
      - service:    detected service name (defaults to "checkout" for the demo)
      - start_time: ISO UTC string or None
      - end_time:   ISO UTC string or None
    """
    service = extract_service(query)
    start_time, end_time = extract_time_range(query)
    return {
        "original": query,
        "service": service or "checkout",   # default to checkout for the demo
        "start_time": start_time,
        "end_time": end_time,
    }
