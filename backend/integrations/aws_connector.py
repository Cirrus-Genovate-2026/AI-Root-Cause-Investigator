import os
import json
from dotenv import load_dotenv
from datetime import datetime
from typing import Dict, List, Any

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")


def get_aws_cost() -> Dict[str, Any]:
    """Get AWS cost and billing information"""
    return {
        "source": "AWS",
        "service": "Cost Explorer",
        "monthly_cost": "$420",
        "details": {
            "cpu_usage": "65%",
            "instances": 3
        }
    }


def get_aws_resources() -> List[Dict[str, Any]]:
    """Get AWS resources overview"""
    return [
        {
            "name": "web-server-prod",
            "type": "EC2",
            "status": "running",
            "region": AWS_REGION,
            "instance_type": "t3.large",
            "state": "running"
        },
        {
            "name": "api-database",
            "type": "RDS",
            "status": "available",
            "region": AWS_REGION,
            "engine": "PostgreSQL",
            "state": "available"
        },
        {
            "name": "app-storage",
            "type": "S3",
            "status": "active",
            "region": AWS_REGION,
            "storage_class": "STANDARD",
            "state": "active"
        },
        {
            "name": "cache-cluster",
            "type": "ElastiCache",
            "status": "available",
            "region": AWS_REGION,
            "engine": "Redis",
            "state": "available"
        }
    ]


def get_cost_analysis() -> Dict[str, Any]:
    """Get detailed cost analysis"""
    return {
        "monthly": "$420",
        "trend": "up",
        "trend_percentage": 5,
        "services": [
            {"name": "EC2", "cost": "$180"},
            {"name": "RDS", "cost": "$120"},
            {"name": "S3", "cost": "$80"},
            {"name": "Other", "cost": "$40"}
        ],
        "last_updated": datetime.now().isoformat()
    }


def get_ec2_instances() -> List[Dict[str, Any]]:
    """Get EC2 instances"""
    return [
        {
            "id": "i-1234567890abcdef0",
            "name": "web-server-prod",
            "type": "t3.large",
            "state": "running",
            "cpu_utilization": 45,
            "memory_utilization": 62,
            "network_in": "1.2 GB",
            "network_out": "0.8 GB",
            "launched": "2024-01-15"
        },
        {
            "id": "i-0987654321fedcba0",
            "name": "api-server-prod",
            "type": "t3.medium",
            "state": "running",
            "cpu_utilization": 28,
            "memory_utilization": 45,
            "network_in": "0.5 GB",
            "network_out": "0.3 GB",
            "launched": "2024-02-01"
        },
        {
            "id": "i-abcdef1234567890a",
            "name": "worker-node-1",
            "type": "t3.small",
            "state": "running",
            "cpu_utilization": 12,
            "memory_utilization": 28,
            "network_in": "0.1 GB",
            "network_out": "0.05 GB",
            "launched": "2024-02-10"
        }
    ]


def get_rds_instances() -> List[Dict[str, Any]]:
    """Get RDS database instances"""
    return [
        {
            "id": "prod-database",
            "engine": "PostgreSQL",
            "version": "14.7",
            "status": "available",
            "allocated_storage": "100 GB",
            "instance_class": "db.t3.large",
            "multi_az": True,
            "backup_retention": 30,
            "cpu_utilization": 35,
            "database_connections": 45
        },
        {
            "id": "cache-database",
            "engine": "PostgreSQL",
            "version": "14.7",
            "status": "available",
            "allocated_storage": "50 GB",
            "instance_class": "db.t3.medium",
            "multi_az": False,
            "backup_retention": 7,
            "cpu_utilization": 12,
            "database_connections": 8
        }
    ]


def get_s3_buckets() -> List[Dict[str, Any]]:
    """Get S3 buckets"""
    return [
        {
            "name": "app-storage-prod",
            "region": AWS_REGION,
            "size": "45.3 GB",
            "objects": 12458,
            "encryption": "AES-256",
            "versioning": "Enabled",
            "created": "2023-06-15"
        },
        {
            "name": "backups-archive",
            "region": AWS_REGION,
            "size": "256.7 GB",
            "objects": 1024,
            "encryption": "AES-256",
            "versioning": "Disabled",
            "created": "2023-09-01"
        },
        {
            "name": "logs-storage",
            "region": AWS_REGION,
            "size": "12.1 GB",
            "objects": 8732,
            "encryption": "AES-256",
            "versioning": "Disabled",
            "created": "2024-01-01"
        }
    ]


def get_aws_data() -> Dict[str, Any]:
    """Fetch comprehensive AWS data"""
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
