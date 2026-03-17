import os
import importlib
import asyncio
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")

app = FastAPI(title="AI Root Cause Investigator - Backend")

# Allow local web UI to access API during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the web directory as static files at /web (use absolute path)
WEB_DIR = Path(__file__).resolve().parent.parent / "web"
if not WEB_DIR.exists():
    raise RuntimeError(f"Web directory not found: {WEB_DIR}")
app.mount("/web", StaticFiles(directory=str(WEB_DIR)), name="web")

# plugin registry: map names to module paths
PLUGIN_REGISTRY = {
    "github": "plugins.github_plugin",
    "postman": "plugins.postman_plugin",
    "aws": "plugins.aws_plugin",
    "azure": "plugins.azure_plugin",
}


class FetchRequest(BaseModel):
    plugin: str
    params: Dict[str, Any] = {}


class AnalyzeRequest(BaseModel):
    query: str
    plugins: List[FetchRequest] = []


def load_plugin(name: str):
    if name not in PLUGIN_REGISTRY:
        raise HTTPException(status_code=404, detail=f"Unknown plugin: {name}")
    module_name = PLUGIN_REGISTRY[name]
    module = importlib.import_module(module_name)
    return module


@app.get("/plugins")
async def list_plugins():
    return {"available": list(PLUGIN_REGISTRY.keys())}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # return JSON for any unhandled exception so clients always get JSON
    return JSONResponse(status_code=500, content={"error": str(exc)})


@app.post("/plugins/fetch")
async def plugin_fetch(req: FetchRequest):
    plugin = load_plugin(req.plugin)
    if not hasattr(plugin, "fetch"):
        raise HTTPException(status_code=500, detail="Plugin missing fetch()")
    # call plugin.fetch(params) - supports async or sync
    fetch_fn = plugin.fetch
    if asyncio.iscoroutinefunction(fetch_fn):
        data = await fetch_fn(req.params)
    else:
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, fetch_fn, req.params)
    return {"plugin": req.plugin, "data": data}


@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    # gather data from requested plugins
    gathered = {}
    for p in req.plugins:
        try:
            plugin = load_plugin(p.plugin)
            fetch_fn = plugin.fetch
            if asyncio.iscoroutinefunction(fetch_fn):
                result = await fetch_fn(p.params)
            else:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, fetch_fn, p.params)
            gathered[p.plugin] = result
        except Exception as e:
            gathered[p.plugin] = {"error": str(e)}

    # Simple heuristic: if OPENAI configured, ask model to summarize and propose root cause
    summary = {
        "query": req.query,
        "gathered_count": {k: len(v) if isinstance(v, (list, dict)) else 1 for k, v in gathered.items()},
    }

    if OPENAI_KEY:
        try:
            import openai

            openai.api_key = OPENAI_KEY
            prompt = f"You are an AI root cause investigator. User asked: {req.query}\n\nData:\n{gathered}\n\nProvide a concise explanation of most likely root causes and steps to investigate and remediate."
            resp = openai.ChatCompletion.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,
            )
            analysis = resp.choices[0].message.content.strip()
        except Exception as e:
            analysis = f"OpenAI call failed: {e}"
    else:
        # fallback naive analysis
        analysis = "No OpenAI key configured. Gathered data keys: " + ",".join(gathered.keys())

    return {"summary": summary, "analysis": analysis, "gathered": gathered}


@app.get("/health")
async def health():
    return {"status": "ok"}
