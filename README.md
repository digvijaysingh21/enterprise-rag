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

- **Step 7 — Password hashing + basic user creation** ✅
  - Added `app/core/security.py` with `hash_password` / `verify_password` using `bcrypt` directly
  - Added `scripts/create_user.py` to create a user outside the API (proves the model end-to-end)
  - Created first admin user, verified in Postgres via psql
  - Added first pytest tests (`tests/test_security.py`) for hashing round-trip + rejection of wrong password

- **Step 8 — Auth endpoints (register/login) + JWT issuing** ✅
  - Added JWT creation/decoding to `app/core/security.py` (`python-jose`)
  - Added `app/api/schemas.py` (register/login/token/user response schemas)
  - Added `app/api/deps.py` with `get_current_user` and `require_admin` dependencies (RBAC foundation)
  - Added `app/api/auth.py` router: `POST /auth/register`, `POST /auth/login`, `GET /auth/me`
  - Verified full flow via `/docs` and PowerShell: register → login → call protected route with token → 401 without token

**Phase 0 status: essentially complete.** One more step to properly close it out (tests + review) before moving to Phase 1.

- **Step 9 — Phase 0 wrap-up** ✅
  - Added `pytest.ini` (`asyncio_mode = auto`) and `tests/conftest.py` (in-process async test client)
  - Added integration tests for the full auth flow: register→login→protected route, wrong password, no token, duplicate email
  - Full test suite passing (unit + integration)
  - Froze dependencies to `requirements.txt`
  - Pushed to GitHub remote

**✅ Phase 0 complete.** Backend skeleton is solid: FastAPI, async Postgres via SQLAlchemy, Alembic migrations, User model with Admin/End User roles, JWT auth with RBAC foundation (`require_admin`), pytest suite (unit + integration), Docker Compose for infra, and full documentation discipline established.

**Known debt (intentionally deferred, not forgotten):**

- Integration tests run against the dev database, not an isolated test DB — needs proper test isolation before the suite grows much further
- No token revocation/refresh-token flow yet — JWTs simply expire after 60 minutes
- No rate limiting on `/auth/login` yet (brute-force protection)

---

## Phase 1 — [next phase: Document Management] ⏳
