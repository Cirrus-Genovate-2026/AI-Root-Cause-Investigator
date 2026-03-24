import os
import importlib
import asyncio
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
import json
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


# Compatibility routes (some UI versions call /api/v1/...)
@app.get("/api/v1/health")
async def health_v1():
    return await health()


@app.get('/api/v1/openai-status')
async def openai_status():
    """Return whether OpenAI key is configured on the server.

    Frontend can use this to show whether server-side LLM analysis will run.
    """
    return {"available": bool(OPENAI_KEY), "model": OPENAI_MODEL if OPENAI_KEY else None}


@app.post('/api/v1/openai-analyze')
async def openai_analyze(payload: Dict[str, Any]):
    """Run an OpenAI analysis on the provided gathered data.

    Expects JSON: { "query": "...", "gathered": {...} }
    Returns: { analysis: "..." }
    """
    if not OPENAI_KEY:
        raise HTTPException(status_code=400, detail='OpenAI API key not configured on server')

    query = payload.get('query') if isinstance(payload, dict) else None
    gathered = payload.get('gathered') if isinstance(payload, dict) else None

    if not query:
        raise HTTPException(status_code=400, detail='query is required')

    # Build a concise prompt including the gathered keys and short excerpts
    try:
        import openai

        openai.api_key = OPENAI_KEY

        def safe_json(obj, max_chars=4000):
            try:
                s = json.dumps(obj, default=str)
                return s[:max_chars]
            except Exception:
                return str(obj)[:max_chars]

        gathered_snip = safe_json(gathered or {})

        system = "You are an AI root cause investigator. Provide a concise root-cause analysis and recommended remediation steps."
        user = f"User query:\n{query}\n\nData (abbreviated):\n{gathered_snip}\n\nProvide: 1) short root cause summary, 2) evidence bullets, 3) next remediation steps (3 max), 4) suggested monitoring/alerts to prevent recurrence."

        # Call OpenAI in a thread to avoid blocking event loop if library is sync
        def call_openai():
            resp = openai.ChatCompletion.create(
                model=OPENAI_MODEL,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                max_tokens=600,
                temperature=0.2,
            )
            return resp

        resp = await asyncio.to_thread(call_openai)
        text = ''
        try:
            text = resp.choices[0].message.content.strip()
        except Exception:
            try:
                text = resp.choices[0].text.strip()
            except Exception:
                text = str(resp)

        return {"analysis": text}
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/v1/analyze-incident")
async def analyze_incident(req: AnalyzeRequest):
    # forward to the newer analyze() handler
    return await analyze(req)


@app.post("/plugins/github/summary")
async def github_summary(req: FetchRequest):
    # expects params: { owner, repo, per_page }
    owner = req.params.get("owner")
    repo = req.params.get("repo")
    if not owner or not repo:
        raise HTTPException(status_code=400, detail="owner and repo required in params")

    plugin = load_plugin("github")
    fetch_fn = plugin.fetch
    if asyncio.iscoroutinefunction(fetch_fn):
        data = await fetch_fn(req.params)
    else:
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, fetch_fn, req.params)

    # If plugin returned an error
    if isinstance(data, dict) and data.get("error"):
        return JSONResponse(status_code=502, content={"error": data.get("error")})

    workflows = []
    if isinstance(data.get("workflows"), dict):
        workflows = data["workflows"].get("workflows", [])
    runs = data.get("workflow_runs") or []

    # build summary per workflow
    summary = {}
    for w in workflows:
        wid = w.get("id")
        wname = w.get("name")
        related = [r for r in runs if r.get("workflow_id") == wid]
        # sort by created_at desc
        related_sorted = sorted(related, key=lambda x: x.get("created_at") or "", reverse=True)
        last = related_sorted[0] if related_sorted else None
        # compute success rate over last 10 runs
        sample = related_sorted[:10]
        succ = sum(1 for r in sample if (r.get("conclusion") == "success"))
        total = len(sample)
        avg_duration = None
        durations = []
        for r in sample:
            start = r.get("run_started_at")
            end = r.get("updated_at") or r.get("run_started_at")
            try:
                from datetime import datetime

                if start and end:
                    fmt = "%Y-%m-%dT%H:%M:%SZ"
                    # some timestamps may include timezone offsets; use fromisoformat when possible
                    try:
                        s_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                        e_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
                        durations.append((e_dt - s_dt).total_seconds())
                    except Exception:
                        pass
            except Exception:
                pass
        if durations:
            avg_duration = sum(durations) / len(durations)

        summary[wname or str(wid)] = {
            "workflow_id": wid,
            "total_recent_runs": total,
            "success_count": succ,
            "success_rate": (succ / total * 100) if total else None,
            "last_run": last,
            "avg_duration_seconds": avg_duration,
        }

    # overall repo-level insights
    total_runs = len(runs)
    overall_success = sum(1 for r in runs if r.get("conclusion") == "success")
    overall_rate = (overall_success / total_runs * 100) if total_runs else None

    return {"summary": summary, "total_runs": total_runs, "overall_success_rate": overall_rate, "raw": data}


@app.post('/api/v1/github-insights')
async def github_insights(payload: Dict[str, Any]):
    owner = payload.get('github_owner') or payload.get('owner')
    repo = payload.get('github_repo') or payload.get('repo')
    per_page = int(payload.get('per_page', 10))
    if not owner or not repo:
        raise HTTPException(status_code=400, detail='github_owner and github_repo required')

    # use plugin to fetch rich data
    plugin = load_plugin('github')
    fetch_fn = plugin.fetch
    params = {'owner': owner, 'repo': repo, 'per_page': per_page}
    if asyncio.iscoroutinefunction(fetch_fn):
        data = await fetch_fn(params)
    else:
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, fetch_fn, params)

    if isinstance(data, dict) and data.get('error'):
        return JSONResponse(status_code=502, content={'error': data.get('error')})

    # build insights expected by frontend
    commits = []
    for c in data.get('commits') or []:
        commit = c.get('commit') if isinstance(c, dict) else None
        commits.append({
            'sha': (c.get('sha')[:7] if c.get('sha') else '') if isinstance(c, dict) else '',
            'message': commit.get('message').split('\n')[0] if commit and commit.get('message') else '',
            'author': (commit.get('author', {}).get('name') if commit else '')
        })

    issues = []
    for i in data.get('issues') or []:
        # some providers may return issue items as JSON strings or dicts; handle both
        item = i
        if isinstance(i, str):
            try:
                import json as _json

                parsed = _json.loads(i)
                if isinstance(parsed, dict):
                    item = parsed
                else:
                    continue
            except Exception:
                # cannot parse string payload, skip
                continue

        if not isinstance(item, dict):
            continue

        issues.append({'number': item.get('number'), 'title': item.get('title'), 'url': item.get('html_url')})

    failed_runs = []
    runs = data.get('workflow_runs') or []
    for r in runs:
        # ensure r is a dict (some APIs may return stringified JSON)
        run_item = r
        if isinstance(r, str):
            try:
                import json as _json

                parsed = _json.loads(r)
                if isinstance(parsed, dict):
                    run_item = parsed
                else:
                    continue
            except Exception:
                continue

        if not isinstance(run_item, dict):
            continue

        if run_item.get('conclusion') and run_item.get('conclusion') != 'success':
            failed_runs.append({
                'name': run_item.get('name') or run_item.get('display_title') or run_item.get('workflow_id'),
                'branch': run_item.get('head_branch'),
                'url': run_item.get('html_url')
            })

    insights = {
        'recent_commits': commits,
        'open_issues': issues,
        'failed_workflow_runs': failed_runs,
        'raw': data,
    }
    return insights


@app.post('/plugins/github/test-token')
async def github_test_token(payload: Dict[str, Any]):
    """Validate a GitHub token by calling the `/user` API and returning scopes.

    Accepts optional JSON `{'token': '...'};` if not provided, uses `GITHUB_TOKEN` from env.
    """
    token = None
    try:
        token = payload.get('token') if isinstance(payload, dict) else None
    except Exception:
        token = None

    if not token:
        token = os.getenv('GITHUB_TOKEN')

    if not token:
        raise HTTPException(status_code=400, detail='No token provided and GITHUB_TOKEN not set')

    # make a lightweight request to GitHub to inspect headers (x-oauth-scopes)
    try:
        import httpx

        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'ai-root-cause-portal/1.0'
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get('https://api.github.com/user', headers=headers)

        scopes_raw = resp.headers.get('x-oauth-scopes') or ''
        scopes = [s.strip() for s in scopes_raw.split(',')] if scopes_raw else []
        login = None
        body = None
        try:
            body = resp.json()
            login = body.get('login')
        except Exception:
            body = None

        return {
            'ok': resp.status_code == 200,
            'status_code': resp.status_code,
            'scopes': scopes,
            'login': login,
            'raw': body,
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={'error': str(e)})


# Simple in-memory event store + queue for live GitHub events received via webhook
GITHUB_EVENTS: List[Dict[str, Any]] = []
GITHUB_EVENT_QUEUE: "asyncio.Queue" = asyncio.Queue()
GITHUB_MAX_EVENTS = 500


@app.post("/webhooks/github")
async def github_webhook(request: Request):
    """Receive GitHub webhook POSTs. Stores event in-memory and pushes to SSE queue.

    To use from GitHub Actions, you can post the full `$GITHUB_EVENT_PATH` payload
    to this endpoint and include header `X-GitHub-Event: <event>`.
    """
    try:
        event_name = request.headers.get("X-GitHub-Event") or request.query_params.get("event")
        body = await request.body()
        try:
            payload = json.loads(body.decode("utf-8")) if body else {}
        except Exception:
            # fallback to raw text
            payload = {"raw": body.decode("utf-8", errors="ignore")}

        evt = {"event": event_name, "payload": payload}
        # attach minimal metadata
        from datetime import datetime

        evt["received_at"] = datetime.utcnow().isoformat() + "Z"

        # append to in-memory store, cap size
        GITHUB_EVENTS.append(evt)
        if len(GITHUB_EVENTS) > GITHUB_MAX_EVENTS:
            GITHUB_EVENTS.pop(0)

        # push to queue for SSE consumers (do not block)
        try:
            GITHUB_EVENT_QUEUE.put_nowait(evt)
        except Exception:
            pass

        return {"received": True, "event": event_name}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/plugins/github/live")
async def github_live(limit: int = 50):
    """Return the most recent GitHub webhook events collected by the portal.

    This is a simple way for the frontend to poll for live events.
    """
    return {"count": len(GITHUB_EVENTS), "events": GITHUB_EVENTS[-limit:]}


@app.get("/sse/github")
async def github_sse(request: Request):
    """Server-Sent Events endpoint that streams GitHub events to connected clients.

    The response is `text/event-stream`. Clients should reconnect on disconnect.
    """

    async def event_generator():
        # Send existing backlog first
        for e in GITHUB_EVENTS[-50:]:
            yield f"data: {json.dumps(e)}\n\n"

        # Then stream new events from the queue
        while True:
            # If client disconnects, stop
            if await request.is_disconnected():
                break
            try:
                evt = await GITHUB_EVENT_QUEUE.get()
                yield f"data: {json.dumps(evt)}\n\n"
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(0.5)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
