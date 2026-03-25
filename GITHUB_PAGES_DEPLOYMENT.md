# GitHub Pages Deployment Guide

## 🚀 Automatic GitHub Pages Deployment

The PlatformIQ portal is now configured to automatically deploy to GitHub Pages via GitHub Actions.

### Live Portal URL
📱 **https://Cirrus-Genovate-2026.github.io/AI-Root-Cause-Investigator/**

## Deployment Architecture

```
GitHub Repository
    ↓
GitHub Actions Workflow (deploy-to-pages.yml)
    ↓
Build & Prepare Static Files
    ↓
GitHub Pages Hosting
    ↓
Static Portal UI (All commits, workflows, PRs, etc. visible)
    ↓
Frontend calls Backend API
    ↓
Backend API (Running separately - can be local or cloud-hosted)
```

## How It Works

1. **Frontend UI** - Deployed to GitHub Pages (static HTML/CSS/JS)
   - Accessible at: `https://Cirrus-Genovate-2026.github.io/AI-Root-Cause-Investigator/`
   - No backend needed for serving the UI
   - Automatically updated on every push to `main`

2. **Backend API** - Keep running separately
   - Local: `http://localhost:8000`
   - Or deploy to: Render, Railway, Heroku, AWS, Azure, etc.

3. **Data Flow**:
   - Browser loads UI from GitHub Pages
   - UI makes API calls to backend
   - Backend fetches GitHub data
   - Data displayed in portal

## Configuration Steps

### Step 1: Enable GitHub Pages (Already Done ✓)
The workflow automatically deploys to GitHub Pages on every push to `main`.

### Step 2: Configure Backend API URL

Edit `backend/templates/index.html` to set your backend URL:

```html
<!-- At the top of script.js or in index.html -->
const API_BASE_URL = 'http://localhost:8000'; // Change to your production backend
```

Or set it in the GitHub Pages config:
```javascript
// In _site/config.js (auto-generated during deploy)
const API_CONFIG = {
  BASE_URL: 'http://your-backend-url.com',
  // ... endpoints
};
```

### Step 3: Backend Deployment Options

#### Option A: Keep Running Locally (Development)
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```
- Access UI: https://Cirrus-Genovate-2026.github.io/AI-Root-Cause-Investigator/
- Backend API: http://localhost:8000
- ⚠️ Only works from your local machine

#### Option B: Deploy Backend to Cloud

**Render.com** (Recommended for quick setup):
1. Go to https://render.com
2. Create new "Web Service"
3. Connect GitHub repository
4. Runtime: Python
5. Build command: `pip install -r backend/requirements.txt`
6. Start command: `cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000`
7. Set environment variables: `GITHUB_TOKEN`, `GITHUB_REPO`
8. Deploy
9. Get URL (e.g., https://platformiq-api.onrender.com)

**Railway.app**:
1. Go to https://railway.app
2. New Project → GitHub Repo
3. Add service → Python
4. Configure similar to above

**AWS/Azure/GCP**: Use Container services (ECS, App Service, Cloud Run)

### Step 4: Update GitHub Pages with Backend URL

After deploying backend, update the API URL:

```bash
# Edit the config in your repo
vi backend/templates/index.html
# Update: const API_BASE_URL = 'https://your-backend-url.com'
git add .
git commit -m "Update backend API URL"
git push
```

The GitHub Pages deployment will automatically update.

## Monitoring Deployments

### Check GitHub Actions Status
1. Go to: https://github.com/Cirrus-Genovate-2026/AI-Root-Cause-Investigator/actions
2. Watch the "Deploy Portal to GitHub Pages" workflow
3. Check logs for any errors

### View Recent Deployments
1. Go to: https://github.com/Cirrus-Genovate-2026/AI-Root-Cause-Investigator/deployments
2. See all GitHub Pages deployments
3. Rollback if needed

## Troubleshooting

### Portal loads but no data showing
- ✓ Check backend API is running
- ✓ Verify backend URL is correct in config
- ✓ Check browser console (F12 → Console tab) for errors
- ✓ Verify GitHub token has proper permissions

### GitHub Pages not updating
- ✓ Check GitHub Actions workflow status
- ✓ Verify push was to `main` branch
- ✓ Wait 1-2 minutes for deployment
- ✓ Force refresh (Ctrl+Shift+R on Windows)

### CORS errors
- ✓ Backend needs CORS headers enabled (already done in FastAPI)
- ✓ Ensure backend URL doesn't have trailing slash
- ✓ Check backend is not blocking requests

## Performance Notes

- GitHub Pages: **Ultra-fast** (CDN cached static files)
- Backend API: Response time depends on GitHub API rate limits
- Recommended: Cache API responses or implement rate limiting

## Security Considerations

✅ **GitHub Pages is safe for:**
- Public portfolio/documentation
- Frontend UI code
- Static files

❌ **Never put on GitHub Pages:**
- Private API keys
- Database credentials
- Tokens (keep in .env backend only)

Current setup: ✓ Secure
- API keys are in backend `.env` only
- GitHub Pages only has frontend code
- Backend handles sensitive data

## Next Steps

1. ✅ Workflow created and committed
2. ⏳ **COMING**: Deploy backend to cloud platform
3. ⏳ **COMING**: Update backend URL in config
4. ⏳ **COMING**: Test end-to-end

## Resources

- GitHub Pages Docs: https://pages.github.com/
- GitHub Actions Docs: https://docs.github.com/actions
- Render.com Docs: https://render.com/docs
- Railway.app Docs: https://docs.railway.app/

---

**Your Portal is now ready to be deployed to GitHub Pages!** 🚀

Current Status:
- ✅ Workflow created
- ✅ Ready to deploy
- ⏳ Waiting for backend to be deployed separately
