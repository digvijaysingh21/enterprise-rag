# Enterprise RAG Platform

Learn-by-doing build of an enterprise-grade RAG system. Two roles: Admin (uploads documents) and End User (queries the knowledge base). Built phase by phase — no phase starts until the previous one works and is documented.

## Progress Log

### Phase 0 — Backend Engineering Foundation

Goal: Get a working FastAPI + Postgres skeleton with basic Admin/User model, before any RAG logic.

- **Step 1 — Hello World API** ✅
  - Created venv, installed FastAPI + Uvicorn
  - Basic `/health` endpoint returning `{"status": "ok"}`
  - Confirmed `/docs` (Swagger UI) auto-generated

- **Step 2 — Project Structure & Repo Hygiene** ✅
  - Restructured into `app/api`, `app/core`, `app/models`, `tests/`
  - Added `.gitignore`, `requirements.txt`, `.env.example`
  - First real git commit

- **Step 3 — Config Management** ⏳ (next)
