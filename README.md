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

- **Step 3 — Config Management** ✅
  - Installed `pydantic-settings`
  - Created `app/core/config.py` with typed `Settings` class loading from `.env`
  - Wired `settings` into `main.py`, `/health` now reflects `ENVIRONMENT` from `.env`
  - Added `.env` (git-ignored) and updated `.env.example`

- **Step 4 — PostgreSQL setup with Docker** ✅
  - Added `docker-compose.yml` with a `postgres:16` service
  - DB credentials moved into `.env` / `.env.example`
  - Verified connection via `docker exec -it rag_postgres psql -U rag_user -d rag_db`

- **Step 5 — Connect FastAPI to PostgreSQL (SQLAlchemy + async engine)** ✅
  - Installed `sqlalchemy[asyncio]` + `asyncpg`
  - Added `DATABASE_URL` as a computed property in `Settings`
  - Created `app/core/database.py` with async engine, session factory, and `get_db()` dependency
  - Added `/health/db` endpoint proving a real DB round-trip via `SELECT 1`

- **Step 6 — First DB model + Alembic migrations** ✅
  - Added shared `Base` (DeclarativeBase) in `app/core/database.py`
  - Created `User` model (UUID pk, email, hashed_password, role enum, is_active, created_at)
  - Initialized Alembic, configured `env.py` for async engine + our models
  - Generated + applied first migration, verified `users` table in Postgres

- **Step 7 — Password hashing + basic user creation (no auth endpoints yet)** ⏳ (next)
