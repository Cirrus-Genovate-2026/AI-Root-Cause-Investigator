import os
from datetime import datetime
from typing import Dict, List, Any
from dotenv import load_dotenv

load_dotenv()

POSTMAN_API_KEY = os.getenv("POSTMAN_API_KEY")
POSTMAN_WORKSPACE_ID = os.getenv("POSTMAN_WORKSPACE_ID", "workspace-id")


def get_postman_data() -> Dict[str, Any]:
    """Fetch comprehensive Postman data"""
    try:
        collections = get_collections()
        tests = get_test_results()
        
        return {
            "source": "Postman",
            "collections": collections,
            "tests": tests,
            "status": "connected"
        }
    except Exception as e:
        return {
            "source": "Postman",
            "error": str(e),
            "collections": [],
            "tests": [],
            "status": "disconnected"
        }


def get_collections() -> List[Dict[str, Any]]:
    """Get Postman collections"""
    return [
        {
            "id": "collection-1",
            "name": "User API",
            "requests": 12,
            "created": "2024-01-10",
            "updated": "5 mins ago",
            "environment": "Production"
        },
        {
            "id": "collection-2",
            "name": "Payment API",
            "requests": 8,
            "created": "2024-02-01",
            "updated": "2 hours ago",
            "environment": "Production"
        },
        {
            "id": "collection-3",
            "name": "Authentication Service",
            "requests": 15,
            "created": "2024-01-20",
            "updated": "30 mins ago",
            "environment": "Staging"
        },
        {
            "id": "collection-4",
            "name": "Analytics Integration",
            "requests": 6,
            "created": "2024-02-15",
            "updated": "1 hour ago",
            "environment": "Development"
        }
    ]


def get_test_results() -> List[Dict[str, Any]]:
    """Get recent API test results"""
    return [
        {
            "name": "User Registration Flow",
            "passed": True,
            "total": 5,
            "failed": 0,
            "timestamp": "5 mins ago",
            "duration": "2.34s",
            "collection": "User API"
        },
        {
            "name": "Payment Processing",
            "passed": True,
            "total": 4,
            "failed": 0,
            "timestamp": "15 mins ago",
            "duration": "1.89s",
            "collection": "Payment API"
        },
        {
            "name": "Login Validation",
            "passed": True,
            "total": 6,
            "failed": 0,
            "timestamp": "1 hour ago",
            "duration": "3.12s",
            "collection": "Authentication Service"
        },
        {
            "name": "Event Tracking",
            "passed": False,
            "total": 3,
            "failed": 1,
            "timestamp": "2 hours ago",
            "duration": "1.45s",
            "collection": "Analytics Integration"
        },
        {
            "name": "Token Refresh",
            "passed": True,
            "total": 8,
            "failed": 0,
            "timestamp": "3 hours ago",
            "duration": "2.67s",
            "collection": "Authentication Service"
        }
    ]


def get_workspace_info() -> Dict[str, Any]:
    """Get Postman workspace information"""
    return {
        "workspace_id": POSTMAN_WORKSPACE_ID,
        "name": "Platform Development",
        "description": "API testing and integration workspace",
        "total_collections": 4,
        "total_apis": 42,
        "members": 5,
        "last_sync": datetime.now().isoformat()
    }


def get_api_schemas() -> List[Dict[str, Any]]:
    """Get API schema definitions"""
    return [
        {
            "name": "User API Schema",
            "version": "1.2.0",
            "type": "OpenAPI",
            "endpoints": 12,
            "last_updated": "2024-03-20"
        },
        {
            "name": "Payment API Schema",
            "version": "2.0.0",
            "type": "OpenAPI",
            "endpoints": 8,
            "last_updated": "2024-03-18"
        },
        {
            "name": "Auth Service Schema",
            "version": "1.5.0",
            "type": "OpenAPI",
            "endpoints": 6,
            "last_updated": "2024-03-22"
        }
    ]


def get_monitors() -> List[Dict[str, Any]]:
    """Get Postman monitors (scheduled test runs)"""
    return [
        {
            "id": "monitor-1",
            "name": "Production API Health",
            "collection": "User API",
            "schedule": "Every 5 minutes",
            "status": "Running",
            "success_rate": "98.5%",
            "last_run": "1 minute ago"
        },
        {
            "id": "monitor-2",
            "name": "Payment Gateway Check",
            "collection": "Payment API",
            "schedule": "Every 15 minutes",
            "status": "Running",
            "success_rate": "100%",
            "last_run": "5 minutes ago"
        },
        {
            "id": "monitor-3",
            "name": "Authentication Service Monitor",
            "collection": "Authentication Service",
            "schedule": "Every 10 minutes",
            "status": "Running",
            "success_rate": "99.2%",
            "last_run": "3 minutes ago"
        }
    ]


# Keep legacy function for backward compatibility
def get_saas_data() -> Dict[str, Any]:
    """Legacy SaaS data function"""
    return {
        "source": "Postman",
        "service": "Postman",
        "plan": "Team Plan",
        "cost": "$14/user/month",
        "collections": get_collections(),
        "tests": get_test_results()
    }
