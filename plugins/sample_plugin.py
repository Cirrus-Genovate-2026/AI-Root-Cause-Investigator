import os
from typing import Any, Dict

"""A sample plugin that either returns mock data or uses Postman/AWS/Azure if configured.
This file provides simple placeholders for AWS, Azure, and Postman connectors. For production,
replace with robust implementations using SDKs and proper pagination/error handling.
"""


async def fetch(params: Dict[str, Any]):
    provider = params.get("provider", "mock")
    if provider == "postman":
        key = os.getenv("POSTMAN_API_KEY")
        if not key:
            return {"error": "POSTMAN_API_KEY not set"}
        # Minimal Postman public API example (user will need to adapt)
        return {"message": "Postman integration placeholder", "params": params}
    if provider == "aws":
        # For AWS we recommend using boto3 with credentials in env or config
        return {"message": "AWS integration placeholder", "params": params}
    if provider == "azure":
        return {"message": "Azure integration placeholder", "params": params}

    # default mock
    return {
        "message": "sample mock data",
        "items": [
            {"id": 1, "type": "log", "text": "service timeout at 2026-03-15T12:01Z"},
            {"id": 2, "type": "metric", "name": "cpu", "value": 94},
        ],
    }
