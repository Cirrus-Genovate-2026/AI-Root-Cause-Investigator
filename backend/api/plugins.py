from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any
from integrations.github_connector import (
    get_github_data, get_recent_commits, get_workflow_runs,
    get_repository_stats, get_pull_requests, get_issues,
    get_branches, get_collaborators
)
from integrations.aws_connector import get_aws_data, get_aws_resources, get_cost_analysis
from integrations.saas_connector import get_postman_data, get_collections, get_test_results
import datetime

router = APIRouter(prefix="/api/plugins", tags=["plugins"])


class QueryRequest(BaseModel):
    question: str


# ========== DASHBOARD ENDPOINTS ==========
@router.get("/dashboard")
async def get_dashboard_data() -> Dict[str, Any]:
    """Get dashboard overview data"""
    return {
        "cost": "$420",
        "incidents": 1,
        "insights": 3,
        "activities": [
            {
                "type": "GitHub",
                "message": "Deployment v2.1.3 completed",
                "time": "2 mins ago"
            },
            {
                "type": "AWS",
                "message": "Auto-scaling triggered on EC2",
                "time": "5 mins ago"
            },
            {
                "type": "AI",
                "message": "Cost optimization recommendation generated",
                "time": "10 mins ago"
            }
        ]
    }


# ========== GITHUB PLUGIN ENDPOINTS ==========
@router.get("/github/data")
async def get_github_plugin_data() -> Dict[str, Any]:
    """Get GitHub plugin data"""
    try:
        data = get_github_data()
        return {
            "commits": data.get("commits", []),
            "workflows": data.get("workflows", []),
            "status": data.get("status")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/github/commits")
async def get_github_commits(limit: int = 5) -> Dict[str, Any]:
    """Get recent GitHub commits"""
    try:
        commits = get_recent_commits(limit)
        return {"commits": commits, "count": len(commits)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/github/workflows")
async def get_github_workflows(limit: int = 5) -> Dict[str, Any]:
    """Get recent GitHub workflows"""
    try:
        workflows = get_workflow_runs(limit)
        return {"workflows": workflows, "count": len(workflows)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/github/stats")
async def get_github_stats() -> Dict[str, Any]:
    """Get GitHub repository statistics"""
    try:
        stats = get_repository_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/github/pull-requests")
async def get_github_prs(state: str = Query("all")) -> Dict[str, Any]:
    """Get GitHub pull requests"""
    try:
        prs = get_pull_requests(limit=20, state=state)
        return {"pull_requests": prs, "count": len(prs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/github/issues")
async def get_github_issues(state: str = Query("open")) -> Dict[str, Any]:
    """Get GitHub issues"""
    try:
        issues = get_issues(limit=20, state=state)
        return {"issues": issues, "count": len(issues)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/github/branches")
async def get_github_branches() -> Dict[str, Any]:
    """Get GitHub branches"""
    try:
        branches = get_branches(limit=20)
        return {"branches": branches, "count": len(branches)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/github/collaborators")
async def get_github_collaborators() -> Dict[str, Any]:
    """Get GitHub collaborators"""
    try:
        collaborators = get_collaborators(limit=30)
        return {"collaborators": collaborators, "count": len(collaborators)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== AWS PLUGIN ENDPOINTS ==========
@router.get("/aws/data")
async def get_aws_plugin_data() -> Dict[str, Any]:
    """Get AWS plugin data"""
    try:
        data = get_aws_data()
        return {
            "resources": data.get("resources", []),
            "costs": data.get("costs", {}),
            "status": data.get("status")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/aws/resources")
async def get_aws_plugin_resources() -> Dict[str, Any]:
    """Get AWS resources"""
    try:
        resources = get_aws_resources()
        return {"resources": resources, "count": len(resources)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/aws/costs")
async def get_aws_plugin_costs() -> Dict[str, Any]:
    """Get AWS cost analysis"""
    try:
        costs = get_cost_analysis()
        return {"costs": costs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== POSTMAN PLUGIN ENDPOINTS ==========
@router.get("/postman/data")
async def get_postman_plugin_data() -> Dict[str, Any]:
    """Get Postman plugin data"""
    try:
        data = get_postman_data()
        return {
            "collections": data.get("collections", []),
            "tests": data.get("tests", []),
            "status": data.get("status")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/postman/collections")
async def get_postman_collections() -> Dict[str, Any]:
    """Get Postman collections"""
    try:
        collections = get_collections()
        return {"collections": collections, "count": len(collections)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/postman/tests")
async def get_postman_tests() -> Dict[str, Any]:
    """Get Postman test results"""
    try:
        tests = get_test_results()
        return {
            "tests": tests,
            "count": len(tests),
            "passed": sum(1 for t in tests if t.get("passed")),
            "failed": sum(1 for t in tests if not t.get("passed"))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== ACTIVITY ENDPOINTS ==========
@router.get("/activity")
async def get_activity() -> Dict[str, Any]:
    """Get recent activity across all plugins"""
    return {
        "recent_activities": [
            {
                "timestamp": datetime.datetime.now().isoformat(),
                "plugin": "GitHub",
                "action": "Commit pushed",
                "description": "feat: Add dashboard plugin system",
                "status": "success"
            },
            {
                "timestamp": datetime.datetime.now().isoformat(),
                "plugin": "AWS",
                "action": "Cost alert",
                "description": "Monthly costs increased by 5%",
                "status": "warning"
            },
            {
                "timestamp": datetime.datetime.now().isoformat(),
                "plugin": "Postman",
                "action": "Test suite run",
                "description": "User API tests passed: 12/12",
                "status": "success"
            }
        ]
    }


# ========== GITHUB TEST ENDPOINT ==========
@router.get("/github/test-public")
async def test_github_public() -> Dict[str, Any]:
    """Test GitHub API with a public repository"""
    import requests
    import os
    from dotenv import load_dotenv
    from pathlib import Path
    
    # Load env
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path)
    
    token = os.getenv("GITHUB_TOKEN")
    headers = {
        "Authorization": f"token {token}" if token else "",
        "Accept": "application/vnd.github+json",
        "User-Agent": "PlatformIQ"
    }
    
    # Test with public repo
    test_url = "https://api.github.com/repos/torvalds/linux/commits?per_page=3"
    response = requests.get(test_url, headers=headers, timeout=10)
    
    return {
        "test_url": test_url,
        "status_code": response.status_code,
        "token_present": bool(token),
        "auth_header": f"{headers['Authorization'][:30]}..." if headers['Authorization'] else "None",
        "response_preview": response.text[:500] if response.status_code != 200 else f"✅ Success - {len(response.json())} commits"
    }


# ========== AI QUERY ENDPOINT ==========
@router.post("/ai/query")
async def query_ai(request: QueryRequest) -> Dict[str, Any]:
    """Process AI query about infrastructure"""
    # This will be enhanced with actual AI processing
    question = request.question.lower()
    
    responses = {
        "cost": "Your monthly AWS costs are $420, up 5% from last month. EC2 instances are your largest expense at $180/month.",
        "deployment": "Your latest deployment (v2.1.3) completed successfully 2 minutes ago. All tests passed.",
        "github": "You have 3 recent commits and 5 active workflows. Current build status: all passing.",
        "postman": "API health is at 98.5%. 42 endpoints are being monitored across 4 collections.",
        "default": "I can help you with infrastructure queries. Ask me about costs, deployments, API health, or resource status!"
    }
    
    for key, response in responses.items():
        if key in question:
            return {"response": response}
    
    return {"response": responses["default"]}
