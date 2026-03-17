import os
from typing import Any, Dict


def fetch(params: Dict[str, Any]):
    """Fetch Azure resources. params: { subscription_id: str (optional) }
    Returns a basic list of resources in the subscription (demo).
    """
    subscription_id = params.get("subscription_id") or os.getenv("AZURE_SUBSCRIPTION_ID")
    if not subscription_id:
        return {"error": "AZURE_SUBSCRIPTION_ID not set; provide subscription_id in params or env"}

    try:
        # import azure SDK lazily to avoid heavy import costs at startup
        from azure.identity import DefaultAzureCredential
        from azure.mgmt.resource import ResourceManagementClient

        cred = DefaultAzureCredential()
        client = ResourceManagementClient(cred, subscription_id)
        resources = []
        for res in client.resources.list():
            resources.append({
                "id": res.id,
                "type": res.type,
                "name": res.name,
                "location": res.location,
            })
        return {"resources": resources}
    except Exception as e:
        return {"error": str(e)}
