import os
import requests
from dotenv import load_dotenv
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

# Load .env from backend folder and parent folders
env_path = Path(__file__).parent.parent / ".env"
if not env_path.exists():
    env_path = Path(__file__).parent.parent.parent / ".env"
    
print(f"Loading .env from: {env_path}")
load_dotenv(env_path)

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPO", "owner/repo")

# Debug: Print what we loaded (hide sensitive token)
token_status = "✅ Token loaded" if GITHUB_TOKEN else "❌ No token"
print(f"{token_status}")
print(f"Repository: {REPO}")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}" if GITHUB_TOKEN else "",
    "Accept": "application/vnd.github+json",
    "User-Agent": "PlatformIQ-GitHub-Connector"
}


def get_github_data() -> Dict[str, Any]:
    """Fetch comprehensive GitHub data including commits and workflows"""
    try:
        commits = get_recent_commits()
        workflows = get_workflow_runs()
        
        return {
            "source": "GitHub",
            "commits": commits,
            "workflows": workflows,
            "status": "connected"
        }
    except Exception as e:
        return {
            "source": "GitHub",
            "error": str(e),
            "commits": [],
            "workflows": [],
            "status": "disconnected"
        }


def get_recent_commits(limit: int = 5) -> List[Dict[str, Any]]:
    """Get recent commits from the repository"""
    try:
        print(f"\n🔍 DEBUG: get_recent_commits() called")
        print(f"   Token exists: {bool(GITHUB_TOKEN)}")
        print(f"   Repository: {REPO}")
        
        if not GITHUB_TOKEN or GITHUB_TOKEN == "your_github_token_here":
            print("⚠️  GitHub token not configured. Using mock data.")
            return _get_mock_commits()
        
        if REPO == "owner/repo":
            print("⚠️  GitHub repository not configured. Using mock data.")
            return _get_mock_commits()
            
        url = f"https://api.github.com/repos/{REPO}/commits?per_page={limit}"
        print(f"   API URL: {url}")
        auth_header = HEADERS.get("Authorization", "")
        print(f"   Auth Header: {auth_header[:20] if auth_header else '❌ No auth'}...")
        
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        print(f"   Response Status: {response.status_code}")
        
        if response.status_code == 401:
            print("❌ GitHub token is invalid or expired")
            return _get_mock_commits()
        elif response.status_code == 404:
            print(f"❌ Repository not found: {REPO}")
            print(f"   Response: {response.text[:200]}")
            return _get_mock_commits()
        elif response.status_code != 200:
            print(f"⚠️  GitHub API error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return _get_mock_commits()
        
        commits_data = response.json()
        print(f"   Commits received: {len(commits_data) if commits_data else 0}")
        
        if not commits_data:
            print("ℹ️  No commits found in repository")
            return _get_mock_commits()
        
        commits = []
        for commit in commits_data[:limit]:
            try:
                message = commit["commit"]["message"].split('\n')[0]
                author = commit["commit"]["author"]["name"]
                date = commit["commit"]["author"]["date"]
                
                commits.append({
                    "message": message,
                    "author": author,
                    "email": commit["commit"]["author"]["email"],
                    "date": date,
                    "sha": commit["sha"][:7],
                    "url": commit["html_url"],
                    "verified": commit.get("commit", {}).get("verification", {}).get("verified", False)
                })
            except KeyError:
                continue
        
        print(f"✅ Fetched {len(commits)} commits from {REPO}")
        return commits if commits else _get_mock_commits()
    except requests.exceptions.Timeout:
        print("⚠️  GitHub API timeout")
        return _get_mock_commits()
    except Exception as e:
        print(f"❌ Error getting commits: {e}")
        return _get_mock_commits()


def get_workflow_runs(limit: int = 5) -> List[Dict[str, Any]]:
    """Get recent workflow runs (CI/CD)"""
    try:
        if not GITHUB_TOKEN or GITHUB_TOKEN == "your_github_token_here":
            print("⚠️  GitHub token not configured. Using mock workflows.")
            return _get_mock_workflows()
        
        if REPO == "owner/repo":
            print("⚠️  GitHub repository not configured. Using mock workflows.")
            return _get_mock_workflows()
            
        url = f"https://api.github.com/repos/{REPO}/actions/runs?per_page={limit}"
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        if response.status_code == 401:
            print("❌ GitHub token is invalid or expired")
            return _get_mock_workflows()
        elif response.status_code == 404:
            print(f"❌ Repository not found: {REPO}")
            return _get_mock_workflows()
        elif response.status_code == 403:
            print("❌ GitHub Actions not enabled or no permissions")
            return _get_mock_workflows()
        elif response.status_code != 200:
            print(f"⚠️  GitHub API error: {response.status_code}")
            return _get_mock_workflows()
        
        data = response.json()
        workflows = []
        
        for run in data.get("workflow_runs", [])[:limit]:
            try:
                workflows.append({
                    "name": run["name"],
                    "status": run["status"],
                    "conclusion": run["conclusion"],
                    "created_at": run["created_at"],
                    "updated_at": run["updated_at"],
                    "head_branch": run["head_branch"],
                    "head_sha": run["head_sha"][:7],
                    "run_number": run["run_number"],
                    "event": run["event"],
                    "url": run["html_url"]
                })
            except KeyError:
                continue
        
        print(f"✅ Fetched {len(workflows)} workflow runs from {REPO}")
        return workflows if workflows else _get_mock_workflows()
    except requests.exceptions.Timeout:
        print("⚠️  GitHub API timeout")
        return _get_mock_workflows()
    except Exception as e:
        print(f"❌ Error getting workflows: {e}")
        return _get_mock_workflows()


def get_repository_stats() -> Dict[str, Any]:
    """Get repository statistics"""
    try:
        if not GITHUB_TOKEN or GITHUB_TOKEN == "your_github_token_here":
            return _get_mock_stats()
        
        if REPO == "owner/repo":
            return _get_mock_stats()
            
        url = f"https://api.github.com/repos/{REPO}"
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        if response.status_code != 200:
            return _get_mock_stats()
        
        repo_data = response.json()
        
        return {
            "name": repo_data["name"],
            "full_name": repo_data["full_name"],
            "description": repo_data["description"],
            "url": repo_data["html_url"],
            "stars": repo_data["stargazers_count"],
            "forks": repo_data["forks_count"],
            "watchers": repo_data["watchers_count"],
            "open_issues": repo_data["open_issues_count"],
            "language": repo_data["language"],
            "license": repo_data["license"]["name"] if repo_data["license"] else "No license",
            "created_at": repo_data["created_at"],
            "updated_at": repo_data["updated_at"],
            "size": f"{repo_data['size'] / 1024:.1f} MB",
            "default_branch": repo_data["default_branch"],
            "is_private": repo_data["private"],
            "visibility": "Private" if repo_data["private"] else "Public"
        }
    except Exception as e:
        print(f"Error getting repo stats: {e}")
        return _get_mock_stats()


def get_failed_workflow_logs() -> Dict[str, Any]:
    """Fetch logs from the most recent failed workflow run for root cause analysis"""
    try:
        if not GITHUB_TOKEN or REPO == "owner/repo":
            return {"error": "GitHub not configured"}

        # Get recent runs and find the latest failed one
        url = f"https://api.github.com/repos/{REPO}/actions/runs?per_page=10"
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return {"error": f"GitHub API error: {response.status_code}"}

        runs = response.json().get("workflow_runs", [])
        failed_run = next((r for r in runs if r.get("conclusion") == "failure"), None)

        if not failed_run:
            return {"message": "No failed workflow runs found. All pipelines are healthy!"}

        run_id = failed_run["id"]

        # Get the jobs for this run
        jobs_url = f"https://api.github.com/repos/{REPO}/actions/runs/{run_id}/jobs"
        jobs_response = requests.get(jobs_url, headers=HEADERS, timeout=10)
        if jobs_response.status_code != 200:
            return {"error": "Could not fetch job details"}

        jobs = jobs_response.json().get("jobs", [])
        failed_steps = []
        for job in jobs:
            for step in job.get("steps", []):
                if step.get("conclusion") == "failure":
                    failed_steps.append({
                        "job": job["name"],
                        "step": step["name"],
                        "conclusion": step["conclusion"]
                    })

        return {
            "workflow_name": failed_run["name"],
            "run_number": failed_run["run_number"],
            "branch": failed_run["head_branch"],
            "triggered_by": failed_run["event"],
            "failed_at": failed_run["updated_at"],
            "url": failed_run["html_url"],
            "failed_steps": failed_steps,
            "commit_message": failed_run.get("head_commit", {}).get("message", "Unknown"),
            "commit_author": failed_run.get("head_commit", {}).get("author", {}).get("name", "Unknown")
        }
    except Exception as e:
        print(f"Error fetching failed workflow logs: {e}")
        return {"error": str(e)}


def get_pull_requests(limit: int = 10, state: str = "all") -> List[Dict[str, Any]]:
    """Get pull requests"""
    try:
        if not GITHUB_TOKEN or GITHUB_TOKEN == "your_github_token_here":
            return []
        
        url = f"https://api.github.com/repos/{REPO}/pulls?state={state}&per_page={limit}"
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        if response.status_code != 200:
            return []
        
        prs = []
        for pr in response.json()[:limit]:
            prs.append({
                "number": pr["number"],
                "title": pr["title"],
                "state": pr["state"],
                "author": pr["user"]["login"],
                "created_at": pr["created_at"],
                "updated_at": pr["updated_at"],
                "url": pr["html_url"],
                "additions": pr.get("additions", 0),
                "deletions": pr.get("deletions", 0),
                "changed_files": pr.get("changed_files", 0)
            })
        
        print(f"✅ Fetched {len(prs)} pull requests")
        return prs
    except Exception as e:
        print(f"Error getting PRs: {e}")
        return []


def get_issues(limit: int = 10, state: str = "open") -> List[Dict[str, Any]]:
    """Get issues"""
    try:
        if not GITHUB_TOKEN or GITHUB_TOKEN == "your_github_token_here":
            return []
        
        url = f"https://api.github.com/repos/{REPO}/issues?state={state}&per_page={limit}"
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        if response.status_code != 200:
            return []
        
        issues = []
        for issue in response.json()[:limit]:
            # Skip pull requests (they're in the issues API too)
            if "pull_request" in issue:
                continue
                
            issues.append({
                "number": issue["number"],
                "title": issue["title"],
                "state": issue["state"],
                "author": issue["user"]["login"],
                "created_at": issue["created_at"],
                "updated_at": issue["updated_at"],
                "labels": [label["name"] for label in issue["labels"]],
                "url": issue["html_url"]
            })
        
        print(f"✅ Fetched {len(issues)} issues")
        return issues
    except Exception as e:
        print(f"Error getting issues: {e}")
        return []


def get_branches(limit: int = 10) -> List[Dict[str, Any]]:
    """Get repository branches"""
    try:
        if not GITHUB_TOKEN or GITHUB_TOKEN == "your_github_token_here":
            return []
        
        url = f"https://api.github.com/repos/{REPO}/branches?per_page={limit}"
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        if response.status_code != 200:
            return []
        
        branches = []
        for branch in response.json()[:limit]:
            branches.append({
                "name": branch["name"],
                "protected": branch["protected"],
                "commit": branch["commit"]["sha"][:7],
                "url": branch["commit"]["url"]
            })
        
        print(f"✅ Fetched {len(branches)} branches")
        return branches
    except Exception as e:
        print(f"Error getting branches: {e}")
        return []


def get_collaborators(limit: int = 20) -> List[Dict[str, Any]]:
    """Get repository collaborators"""
    try:
        if not GITHUB_TOKEN or GITHUB_TOKEN == "your_github_token_here":
            return []
        
        url = f"https://api.github.com/repos/{REPO}/collaborators?per_page={limit}"
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        if response.status_code != 200:
            return []
        
        collaborators = []
        for collab in response.json()[:limit]:
            collaborators.append({
                "login": collab["login"],
                "avatar_url": collab["avatar_url"],
                "profile_url": collab["html_url"],
                "contribution": collab.get("contributions", 0),
                "permission": collab.get("role_name", "Unknown")
            })
        
        print(f"✅ Fetched {len(collaborators)} collaborators")
        return collaborators
    except Exception as e:
        print(f"Error getting collaborators: {e}")
        return []



def _get_mock_commits() -> List[Dict[str, Any]]:
    """Return mock commit data for demonstration"""
    return [
        {
            "message": "feat: Add new dashboard plugin system",
            "author": "Alice Johnson",
            "email": "alice@example.com",
            "date": datetime.now().isoformat(),
            "sha": "abc1234",
            "url": "#"
        },
        {
            "message": "fix: Resolve AWS connector timeout issue",
            "author": "Bob Smith",
            "email": "bob@example.com",
            "date": datetime.now().isoformat(),
            "sha": "def5678",
            "url": "#"
        },
        {
            "message": "docs: Update API documentation",
            "author": "Charlie Dev",
            "email": "charlie@example.com",
            "date": datetime.now().isoformat(),
            "sha": "ghi9012",
            "url": "#"
        }
    ]


def _get_mock_workflows() -> List[Dict[str, Any]]:
    """Return mock workflow data for demonstration"""
    return [
        {
            "name": "Build and Deploy",
            "status": "completed",
            "conclusion": "success",
            "created_at": datetime.now().isoformat(),
            "url": "#"
        },
        {
            "name": "Unit Tests",
            "status": "completed",
            "conclusion": "success",
            "created_at": datetime.now().isoformat(),
            "url": "#"
        },
        {
            "name": "Code Quality Check",
            "status": "in_progress",
            "conclusion": None,
            "created_at": datetime.now().isoformat(),
            "url": "#"
        }
    ]


def _get_mock_stats() -> Dict[str, Any]:
    """Return mock repository statistics"""
    return {
        "name": "Cloud-craft-AI",
        "stars": 42,
        "forks": 12,
        "watchers": 8,
        "language": "Python",
        "description": "AI-powered cloud integration platform",
        "url": "#"
    }