# GitHub Integration Setup Guide

This guide will help you connect your GitHub repository to the PlatformIQ portal to see real-time commits, workflows, pull requests, and issues.

## 📋 Prerequisites

- GitHub account
- A GitHub repository you own or have access to
- Administrator or push access to the repository

## 🔑 Step 1: Generate a GitHub Personal Access Token

1. Go to GitHub Settings: https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Give your token a descriptive name, e.g., `PlatformIQ-Portal`
4. Set **Expiration** to 90 days or No expiration
5. Select the following **scopes**:
   - ✅ `repo` - Full control of private repositories
   - ✅ `read:repo_hook` - Read repository webhooks
   - ✅ `read:actions` - Read GitHub Actions workflows
   - ✅ `read:org` - Read organization data (optional)
   - ✅ `read:user` - Read user profile (optional)

6. Click **"Generate token"**
7. **Copy the token immediately** (you won't see it again!)

## 📝 Step 2: Configure Environment Variables

1. Navigate to the backend folder:
   ```bash
   cd backend
   ```

2. Create a `.env` file (copy from `.env.example` if it exists):
   ```bash
   cp .env.example .env
   ```

3. Edit the `.env` file and add your GitHub credentials:
   ```env
   # GitHub API Token (from step 1)
   GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

   # GitHub Repository (format: owner/username)
   # Examples:
   # GITHUB_REPO=microsoft/vscode
   # GITHUB_REPO=torvalds/linux
   # GITHUB_REPO=your-username/your-repo
   GITHUB_REPO=your-username/your-repo
   ```

4. Save the `.env` file

## ✅ Step 3: Verify the Integration

1. **Restart the backend** (if it's running):
   ```bash
   # Kill the current process with Ctrl+C or restart terminal
   # Then run:
   python -m uvicorn main:app --reload
   ```

2. **Check the logs** for connection confirmation:
   ```
   ✅ Fetched 5 commits from owner/repo
   ✅ Fetched 5 workflow runs from owner/repo
   ```

3. **Open the portal** in browser: http://localhost:8000

4. **Navigate to the GitHub plugin** and click "Sync"

5. **You should see**:
   - Real commits from your repository
   - Actual GitHub Actions workflows
   - Pull requests (if any)
   - Issues (if any)
   - Repository branches
   - Collaborators

## 🐛 Troubleshooting

### Issue: "GitHub token not configured"
**Solution**: Make sure your `.env` file has `GITHUB_TOKEN` set correctly and the backend is restarted after changes.

### Issue: "Repository not found"
**Solution**: Double-check the repository format is `owner/repo` (e.g., `torvalds/linux`, not just `linux`)

### Issue: "GitHub token is invalid or expired"
**Solution**: Generate a new token from https://github.com/settings/tokens and update your `.env` file.

### Issue: "GitHub Actions not enabled or no permissions"
**Solution**: Ensure GitHub Actions is enabled in your repository settings and your token has `read:actions` scope.

### Issue: Still seeing mock data
**Solution**: 
- Verify your `.env` file is in the `backend` folder
- Restart Python/FastAPI completely
- Check browser console for any errors
- Verify tokens don't have leading/trailing spaces

## 📊 What Data Can You See?

Once connected, the GitHub plugin displays:

| Category | Details |
|----------|---------|
| **Commits** | Message, author, date, SHA, verification status |
| **Workflows** | Name, status, conclusion, branch, run number, event type |
| **Pull Requests** | Title, author, state, additions/deletions, changed files |
| **Issues** | Title, author, state, labels, attachments |
| **Branches** | Branch name, protection status, latest commit |
| **Repository** | Stars, forks, watchers, language, description |

## 🔐 Security Notes

- Never commit your `.env` file to GitHub (add to `.gitignore`)
- Keep your GitHub token secret
- You can revoke tokens anytime at https://github.com/settings/tokens
- Use fine-grained personal access tokens for production (GitHub feature)

## 📚 More Info

- GitHub API Docs: https://docs.github.com/en/rest
- Personal Access Tokens: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
- GitHub Actions Docs: https://docs.github.com/en/actions

## ✨ Next Steps

After setting up GitHub:
1. Connect your AWS account for cloud monitoring
2. Link your Postman workspace for API testing
3. Configure AI assistant for infrastructure queries
