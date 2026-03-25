import os
import boto3
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import Dict, List, Any
from pathlib import Path

env_path = Path(__file__).parent.parent.parent / ".env"
if not env_path.exists():
    env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

CREDENTIALS = dict(
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)


def _client(service: str, region: str = None):
    return boto3.client(service, **{**CREDENTIALS, "region_name": region or AWS_REGION})


def get_ec2_instances() -> List[Dict[str, Any]]:
    try:
        ec2 = _client("ec2")
        response = ec2.describe_instances(
            Filters=[{"Name": "instance-state-name", "Values": ["running", "stopped", "pending"]}]
        )
        instances = []
        for reservation in response.get("Reservations", []):
            for inst in reservation.get("Instances", []):
                name = next((t["Value"] for t in inst.get("Tags", []) if t["Key"] == "Name"), inst["InstanceId"])
                instances.append({
                    "id": inst["InstanceId"],
                    "name": name,
                    "type": inst["InstanceType"],
                    "state": inst["State"]["Name"],
                    "region": AWS_REGION,
                    "launch_time": inst["LaunchTime"].isoformat()
                })
        return instances
    except Exception as e:
        print(f"EC2 error: {e}")
        return []


def get_rds_instances() -> List[Dict[str, Any]]:
    try:
        rds = _client("rds")
        response = rds.describe_db_instances()
        instances = []
        for db in response.get("DBInstances", []):
            instances.append({
                "id": db["DBInstanceIdentifier"],
                "engine": f"{db['Engine']} {db['EngineVersion']}",
                "status": db["DBInstanceStatus"],
                "instance_class": db["DBInstanceClass"],
                "multi_az": db["MultiAZ"],
                "allocated_storage": f"{db['AllocatedStorage']} GB",
                "region": AWS_REGION
            })
        return instances
    except Exception as e:
        print(f"RDS error: {e}")
        return []


def get_s3_buckets() -> List[Dict[str, Any]]:
    try:
        s3 = _client("s3", region="us-east-1")
        response = s3.list_buckets()
        buckets = []
        for bucket in response.get("Buckets", []):
            buckets.append({
                "name": bucket["Name"],
                "created": bucket["CreationDate"].isoformat()
            })
        return buckets
    except Exception as e:
        print(f"S3 error: {e}")
        return []


def get_cost_analysis() -> Dict[str, Any]:
    try:
        ce = _client("ce", region="us-east-1")
        end = datetime.today().strftime("%Y-%m-%d")
        start = (datetime.today().replace(day=1)).strftime("%Y-%m-%d")

        response = ce.get_cost_and_usage(
            TimePeriod={"Start": start, "End": end},
            Granularity="MONTHLY",
            Metrics=["UnblendedCost"],
            GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}]
        )

        total = 0.0
        services = []
        for group in response["ResultsByTime"][0].get("Groups", []):
            cost = float(group["Metrics"]["UnblendedCost"]["Amount"])
            if cost > 0:
                services.append({"name": group["Keys"][0], "cost": f"${cost:.2f}"})
                total += cost

        services.sort(key=lambda x: float(x["cost"][1:]), reverse=True)

        return {
            "monthly": f"${total:.2f}",
            "services": services[:6],
            "period": f"{start} to {end}",
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Cost Explorer error: {e}")
        return {"monthly": "N/A", "services": [], "error": str(e)}


def get_aws_resources() -> List[Dict[str, Any]]:
    resources = []
    for inst in get_ec2_instances():
        resources.append({"name": inst["name"], "type": "EC2", "status": inst["state"], "region": inst["region"]})
    for db in get_rds_instances():
        resources.append({"name": db["id"], "type": "RDS", "status": db["status"], "region": db["region"]})
    for bucket in get_s3_buckets():
        resources.append({"name": bucket["name"], "type": "S3", "status": "active", "region": "global"})
    return resources


def get_aws_cost() -> Dict[str, Any]:
    costs = get_cost_analysis()
    ec2_count = len(get_ec2_instances())
    rds_count = len(get_rds_instances())
    s3_count = len(get_s3_buckets())
    return {
        "source": "AWS",
        "monthly_cost": costs.get("monthly", "N/A"),
        "cost_by_service": costs.get("services", []),
        "ec2_instances": ec2_count,
        "rds_instances": rds_count,
        "s3_buckets": s3_count
    }


def get_aws_data() -> Dict[str, Any]:
    try:
        return {
            "source": "AWS",
            "resources": get_aws_resources(),
            "costs": get_cost_analysis(),
            "status": "connected"
        }
    except Exception as e:
        return {
            "source": "AWS",
            "error": str(e),
            "resources": [],
            "costs": {},
            "status": "disconnected"
        }
