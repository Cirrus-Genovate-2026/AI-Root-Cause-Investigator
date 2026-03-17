# AI Root Cause Investigator — Demo Portal

This project is a minimal demo of an AI-powered platform intelligence system with a plugin-based architecture.

Quick start (Windows):

1. Copy `.env.example` to `.env` and fill credentials (GitHub token, OpenAI key, AWS/Azure as needed).

2. Create and activate a Python virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. Run the backend (from project root):

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

4. Open the demo portal in your browser:

http://127.0.0.1:8000/web/index.html

Notes:
- This is a demo scaffold. The `plugins/sample_plugin.py` contains placeholders for AWS, Azure, and Postman connectors. Replace with production-grade connectors using respective SDKs (`boto3`, `azure` SDKs, Postman APIs).
- The `plugins/github_plugin.py` fetches commits and issues using the `GITHUB_TOKEN` environment variable.
- The `/analyze` endpoint will call OpenAI if `OPENAI_API_KEY` is set; otherwise it returns a simple fallback.

Next steps (suggested):
- Harden plugin implementations, add pagination and error handling.
- Add authentication to web UI and backend.
- Add background collectors, caching, and scheduling to fetch telemetry continuously.
- Add UI components to visualize timelines, metrics and correlated events.
# Unified-AI-Platform
AI-Powered Unified Platform for Infrastructure, DevOps, and Network Intelligence - (Consolidate fragmented data across DevOps, Security, and Observability tools into a single "Natural Language" interface. Enable engineers to query system health, dependencies, and ownership instantly—eliminating manual dashboard-hopping .
