"""
backend/main.py — FastAPI application entry point

Run from the project root:
  uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000

Then open: http://127.0.0.1:8000
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.routes.incidents import router as incidents_router

load_dotenv()

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="AI Incident Root Cause Investigator",
    description=(
        "AI-powered root cause analysis for cloud incidents. "
        "Correlates logs, metrics, deployments and GitHub data."
    ),
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# ---------------------------------------------------------------------------
# CORS  (permissive for local demo; tighten for production)
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

app.include_router(incidents_router, prefix="/api/v1", tags=["incidents"])

# ---------------------------------------------------------------------------
# Global error handler  — always return JSON so the UI can parse it
# ---------------------------------------------------------------------------

@app.exception_handler(Exception)
async def _global_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "type": type(exc).__name__},
    )

# ---------------------------------------------------------------------------
# Static files  — serve the web/ directory at "/"
# ---------------------------------------------------------------------------

_WEB_DIR = Path(__file__).resolve().parent.parent / "web"
if _WEB_DIR.exists():
    app.mount("/", StaticFiles(directory=str(_WEB_DIR), html=True), name="web")
