# AI Incident Root Cause Investigator

An AI-powered demo platform that correlates **logs, metrics, deployments and live GitHub data** to identify the root cause of cloud incidents — and explains it in plain English.

---

## Project Structure

```
ai-incident-root-cause-investigator/
│
├── backend/                        ← FastAPI backend (new entry point)
│   ├── main.py                     ← App factory, CORS, static file mount
│   ├── routes/
│   │   └── incidents.py            ← GET /health, POST /analyze-incident, GET /timeline
│   ├── services/
│   │   ├── data_loader.py          ← Loads JSON data + fetches GitHub via plugin
│   │   ├── parser.py               ← Extracts service name & time range from query
│   │   ├── correlation_engine.py   ← Rule-based root cause rules
│   │   ├── evidence_builder.py     ← Builds structured evidence package
│   │   └── llm_summary.py          ← LLM prompt, OpenAI/Azure call, fallback
│   └── data/                       ← Mock data (checkout failure scenario)
│       ├── logs.json
│       ├── metrics.json
│       ├── deployments.json
│       └── alerts.json
│
├── plugins/
│   ├── github_plugin.py            ← Live GitHub API: commits, workflow runs, deployments
│   ├── aws_plugin.py               ← AWS EC2/S3 (uses boto3)
│   ├── azure_plugin.py             ← Azure resources (uses azure-mgmt-resource)
│   └── postman_plugin.py           ← Postman collections/workspaces
│
├── web/
│   └── index.html                  ← Incident investigation UI (vanilla HTML/JS)
│
├── app/
│   └── main.py                     ← Legacy plugin-explorer entry point (kept for reference)
│
├── requirements.txt
├── .env.example
└── README.md
```

---

## Quick Start (Windows)

### 1 — Clone and set up Python environment

```powershell
git clone <your-repo-url>
cd ai-incident-root-cause-investigator

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2 — Configure environment variables

```powershell
Copy-Item .env.example .env
# Edit .env and fill in your keys
```

Minimum required keys:

| Key | Purpose |
|-----|---------|
| `GITHUB_TOKEN` | Read-only PAT for live GitHub data (avoids rate limits) |
| `OPENAI_API_KEY` **or** `AZURE_OPENAI_API_KEY` + `AZURE_OPENAI_ENDPOINT` | AI explanation layer |

The system works **without any API keys** using the built-in rule-based fallback and mock data.

### 3 — Run the backend

```powershell
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### 4 — Open the UI

```
http://127.0.0.1:8000
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/health` | Health check |
| `POST` | `/api/v1/analyze-incident` | Full root cause analysis pipeline |
| `GET` | `/api/v1/timeline?service=checkout` | Chronological event timeline |
| `GET` | `/api/docs` | Interactive Swagger UI |

### Example: Analyze an incident

```bash
curl -X POST http://127.0.0.1:8000/api/v1/analyze-incident \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Why did the checkout service fail today?",
    "service": "checkout",
    "github_owner": "your-org",
    "github_repo":  "your-repo"
  }'
```

---

## How It Works

```
User Query
    │
    ▼
parser.py          ─── extract service name + time range
    │
    ▼
data_loader.py     ─── load logs + metrics + deployments + alerts (JSON)
                   ─── fetch live GitHub: commits, workflow_runs, deployments
    │
    ▼
correlation_engine ─── run 8 root-cause rules (thresholds, timing, patterns)
    │
    ▼
evidence_builder   ─── build unified evidence: timeline, metrics summary,
                        GitHub insights, finding list
    │
    ▼
llm_summary        ─── prompt LLM → structured JSON: root cause, confidence,
                        next steps, prevention
    │
    ▼
/api/v1/analyze-incident response
```

### Root Cause Rules

| Rule | Trigger |
|------|---------|
| `FAILED_DEPLOYMENT` | Deployment/workflow status = failure |
| `GITHUB_CI_FAILURE` | GitHub Actions workflow run concluded failure |
| `DEPLOYMENT_BEFORE_INCIDENT` | Deployment within 30 min before first alert |
| `DATABASE_ERRORS` | Log keywords: timeout, pool exhausted, connection refused |
| `HIGH_ERROR_RATE` | Error rate metric > 10% |
| `CPU_EXHAUSTION` | CPU metric > 80% |
| `HIGH_LATENCY` | Response time metric > 1000ms |
| `MEMORY_PRESSURE` | Memory metric > 85% |

---

## Demo Scenario

The built-in mock data simulates a **checkout service failure on 2026-03-19**:

- 09:58 — Deployment `v2.1.3` starts (PR #142: Stripe v3 integration, changed DB pool config)
- 10:02 — Deployment completes
- 10:05 — Latency warnings appear (p99 = 850ms)
- 10:09 — DB connection pool exhausted (50/50)
- 10:10 — Payment failures cascade
- 10:12 — Circuit breaker opens, error rate 48%
- 10:15 — Service health check fails (503)
- 10:20 — SRE rolls back to v2.1.2
- 10:25 — Service restored

**Root cause:** `v2.1.3` changed the DB connection pool max from 20 → 50, exhausting the database server's connection limit under production traffic.

---

## GitHub Integration

When you provide `github_owner` and `github_repo`, the system fetches:

- **Commits** → Recent code changes for LLM context
- **Workflow Runs** → Failed CI runs are flagged as high-confidence findings
- **Deployments** → Matched against incident timing
- **Issues** → Open bugs related to the service
- **Releases** → Version comparison

> Set `GITHUB_TOKEN` in `.env` to a read-only Personal Access Token (PAT) to avoid the 60 req/hour unauthenticated rate limit.

---

## Legacy Entry Point

The original plugin-explorer UI is still available at:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
# then open http://127.0.0.1:8000/web/index.html  (old UI)
```

