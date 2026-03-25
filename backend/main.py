from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from api.query import router as query_router
from api.plugins import router as plugins_router
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
if not env_path.exists():
    env_path = Path(__file__).parent.parent / ".env"
    
print(f"🔧 Loading environment from: {env_path}")
load_dotenv(env_path)

print("=" * 50)
print("🚀 PLATFORMIQ BACKEND STARTING UP")
print(f"✅ GitHub Token: {'✓ Present' if os.getenv('GITHUB_TOKEN') else '❌ Missing'}")
print(f"✅ GitHub Repo: {os.getenv('GITHUB_REPO', '❌ Not configured')}")
print("=" * 50)

app = FastAPI(
    title="PlatformIQ - AI Integration Portal",
    description="AI-powered cloud integration and monitoring platform",
    version="2.0.0"
)

# ========== CORS CONFIGURATION ==========
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== API ROUTES ==========
app.include_router(query_router)
app.include_router(plugins_router)

# ========== DASHBOARD ENDPOINT ==========
@app.get("/api/dashboard")
def get_dashboard():
    """Get dashboard data"""
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

# ========== STATIC FILES ==========
# Mount static files BEFORE other routes
base_dir = Path(__file__).parent
static_dir = base_dir / "static"

if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# ========== HTML MAIN ROUTE ==========
@app.get("/api/debug/config")
async def debug_config():
    """Debug endpoint to verify configuration"""
    github_token = os.getenv("GITHUB_TOKEN", "❌ Not set")
    github_token_masked = f"...{github_token[-8:]}" if github_token and github_token != "❌ Not set" else github_token
    
    return {
        "status": "debug",
        "github_token": github_token_masked,
        "github_repo": os.getenv("GITHUB_REPO", "❌ Not set"),
        "env_file_found": env_path.exists(),
        "env_file_path": str(env_path),
        "current_directory": str(Path.cwd())
    }

@app.get("/")
async def serve_root():
    """Serve the main HTML page"""
    template_path = base_dir / "templates" / "index.html"
    if template_path.exists():
        return FileResponse(str(template_path), media_type="text/html")
    else:
        return HTMLResponse("""
        <html>
            <body style="background: #0f172a; color: #f1f5f9; font-family: Arial; padding: 20px;">
                <h1>PlatformIQ Portal</h1>
                <p>Portal is loading... If you don't see the dashboard, please refresh the page.</p>
                <p><a href="/docs" style="color: #3b82f6;">API Documentation</a></p>
            </body>
        </html>
        """)
