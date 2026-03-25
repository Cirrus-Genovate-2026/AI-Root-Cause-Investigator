#!/usr/bin/env python3
import requests
import json

token = "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"
headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github+json",
    "User-Agent": "PlatformIQ-Diagnostic"
}

print("=" * 60)
print("🔐 GITHUB TOKEN DIAGNOSTIC")
print("=" * 60)

# 1. Get user info
print("\n1️⃣  USER INFO:")
try:
    r = requests.get("https://api.github.com/user", headers=headers, timeout=10)
    if r.status_code == 200:
        user = r.json()
        print(f"   ✓ Login: {user.get('login')}")
        print(f"   ✓ Name: {user.get('name')}")
        print(f"   ✓ Public Repos: {user.get('public_repos')}")
        print(f"   ✓ Total Private Repos: {user.get('total_private_repos')}")
    else:
        print(f"   ✗ Error: {r.status_code}")
except Exception as e:
    print(f"   ✗ Exception: {e}")

# 2. Get organizations
print("\n2️⃣  ORGANIZATIONS:")
try:
    r = requests.get("https://api.github.com/user/orgs", headers=headers, timeout=10)
    if r.status_code == 200:
        orgs = r.json()
        if orgs:
            print(f"   Found {len(orgs)} organizations:")
            for org in orgs:
                print(f"   ✓ {org.get('login')}")
        else:
            print("   ✗ No organizations found")
    else:
        print(f"   ✗ Error: {r.status_code}")
except Exception as e:
    print(f"   ✗ Exception: {e}")

# 3. Get repositories (user)
print("\n3️⃣  REPOSITORIES (excluding org):")
try:
    r = requests.get("https://api.github.com/user/repos?per_page=50&type=owner", headers=headers, timeout=10)
    if r.status_code == 200:
        repos = r.json()
        print(f"   Found {len(repos)} repositories")
        if repos:
            for repo in repos:
                print(f"   ✓ {repo.get('full_name')} (Private: {repo.get('private')})")
        else:
            print("   ℹ️  No results (you may not have any personal repos)")
    else:
        print(f"   ✗ Error: {r.status_code}")
except Exception as e:
    print(f"   ✗ Exception: {e}")

# 4. Test specific organization repository
print("\n4️⃣  TEST SPECIFIC REPO: Cirrus-Genovate-2026/AI-Root-Cause-Investigator")
try:
    r = requests.get(
        "https://api.github.com/repos/Cirrus-Genovate-2026/AI-Root-Cause-Investigator",
        headers=headers,
        timeout=10
    )
    if r.status_code == 200:
        repo = r.json()
        print(f"   ✅ ACCESSIBLE!")
        print(f"   Full Name: {repo.get('full_name')}")
        print(f"   Private: {repo.get('private')}")
        print(f"   Description: {repo.get('description', 'N/A')}")
        
        # Try to get commits
        print("\n5️⃣  GET COMMITS FROM REPO:")
        r2 = requests.get(
            f"https://api.github.com/repos/Cirrus-Genovate-2026/AI-Root-Cause-Investigator/commits?per_page=5",
            headers=headers,
            timeout=10
        )
        if r2.status_code == 200:
            commits = r2.json()
            print(f"   ✅ Got {len(commits)} commits")
            if commits:
                print(f"   Latest: {commits[0].get('commit', {}).get('message', 'N/A')[:60]}")
        else:
            print(f"   ❌ Status: {r2.status_code}")
            print(f"   Response: {r2.text[:200]}")
    else:
        print(f"   ❌ NOT ACCESSIBLE")
        print(f"   Status: {r.status_code}")
        print(f"   Response: {r.text[:200]}")
except Exception as e:
    print(f"   ✗ Exception: {e}")

print("\n" + "=" * 60)
