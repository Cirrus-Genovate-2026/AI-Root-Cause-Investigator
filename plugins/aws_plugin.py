import os
from typing import Any, Dict


def fetch(params: Dict[str, Any]):
    """Fetch AWS resources. params: { resource: 'ec2'|'s3', region: optional }
    Returns a dict with basic resource lists for demo purposes.
    """
    region = params.get("region") or os.getenv("AWS_REGION") or "us-east-1"
    resource = params.get("resource", "ec2")

    try:
        # import boto3 lazily to avoid slow startup/import-time overhead
        import boto3
        from botocore.exceptions import BotoCoreError, ClientError

        if resource == "ec2":
            ec2 = boto3.client("ec2", region_name=region)
            resp = ec2.describe_instances(MaxResults=20)
            instances = []
            for r in resp.get("Reservations", []):
                for i in r.get("Instances", []):
                    instances.append({
                        "InstanceId": i.get("InstanceId"),
                        "State": i.get("State", {}).get("Name"),
                        "InstanceType": i.get("InstanceType"),
                    })
            return {"ec2_instances": instances}

        if resource == "s3":
            s3 = boto3.client("s3", region_name=region)
            resp = s3.list_buckets()
            buckets = [b.get("Name") for b in resp.get("Buckets", [])]
            return {"s3_buckets": buckets}

        return {"error": "unknown resource type"}

    except Exception as e:
        return {"error": str(e)}
