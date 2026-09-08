# Technical Knowledge Log

Concepts learned during this build — what it is, when to use it, why it matters. Ordered by when it came up.

---

## FastAPI

**What:** A Python web framework for building APIs, built on Starlette (ASGI) + Pydantic.
**Why we use it:** Async-native (important for I/O-heavy work like calling LLMs/vector DBs later), automatic request validation via Pydantic, and auto-generates interactive API docs (`/docs`) from your code with zero extra work.
**When it matters:** Every backend endpoint in this project goes through FastAPI.

## Uvicorn

**What:** An ASGI server — the actual process that runs your FastAPI app and handles incoming HTTP connections.
**Why we use it:** FastAPI defines _what_ happens on a request; Uvicorn is _what actually listens on a port and serves it_. `--reload` auto-restarts the server on code changes, useful only in development (never use `--reload` in production).

## Virtual Environments (venv)

**What:** An isolated Python installation + package set, scoped to one project.
**Why:** Prevents dependency conflicts between projects (e.g. this project needs FastAPI 0.11x, another project might need something incompatible). Never install project dependencies globally.

## requirements.txt

**What:** A pinned list of exact package versions (`pip freeze > requirements.txt`).
**Why:** Reproducibility — anyone (including future-you on a new machine) can run `pip install -r requirements.txt` and get the identical environment. Without pinning, "works on my machine" bugs creep in silently as libraries update.

## .env / .env.example pattern

**What:** `.env` holds real secrets/config (API keys, DB passwords) and is never committed. `.env.example` lists the _variable names_ with placeholder/blank values, and IS committed, so collaborators know what config the app expects.
**Why:** Secrets must never end up in git history — even a private repo's history is a leak waiting to happen if it ever goes public or gets shared.

## .gitignore

**What:** Tells git which files/folders to never track (venv, cache files, secrets, compiled files).
**Why:** Keeps the repo clean and prevents accidentally committing machine-specific or sensitive files.

## Pydantic Settings (BaseSettings)

**What:** A Pydantic subclass that automatically loads and validates config from environment variables / a .env file into typed Python attributes.
**Why:** Centralizes all config in one typed, validated place instead of scattered `os.environ.get()` calls with no validation. Fails fast at startup if config is wrong, rather than failing mysteriously mid-request.
**When it matters:** Every setting the app needs — DB URLs, API keys, feature flags — should live in `Settings`, never hardcoded inline.

## Docker Compose

**What:** A tool for defining and running multi-container Docker setups from a single `docker-compose.yml` file, instead of long `docker run` commands.
**Why:** As this project grows (Postgres, ChromaDB, workers, etc.), we'll need several containers running together with shared networking. Compose declares the whole stack as one file, version-controlled alongside the code.
**When it matters:** Any time we add a new piece of infrastructure (vector DB, Redis cache, MinIO), it goes into this same `docker-compose.yml` as a new service.

## Docker Volumes

**What:** Persistent storage that lives outside the container's filesystem (`pgdata` in our compose file).
**Why:** Containers are ephemeral — if you remove and recreate the Postgres container without a volume, all your data is gone. The volume survives container recreation.
**When it matters:** Any stateful service (databases, vector stores) needs a volume, or you'll lose data on every `docker compose down`.

## Environment variables for DB credentials

**What:** Postgres username/password/db name are read by the container from environment variables at first startup (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`).
**Why:** Same reasoning as app config — credentials never get hardcoded into `docker-compose.yml` directly in a real setup; they come from `.env`, which Docker Compose reads automatically if present in the same directory.

## SQLAlchemy Async Engine

**What:** SQLAlchemy 2.x's async API (`create_async_engine`, `AsyncSession`) for running database queries without blocking the event loop.
**Why:** FastAPI is async-native. If you use SQLAlchemy's classic sync engine inside an `async def` route, that DB call blocks the whole event loop while it waits — killing concurrency. The async engine lets FastAPI handle other requests while waiting on the DB.
**When it matters:** Every DB-touching route in this project uses `async def` + the async session, never the sync API.

## asyncpg

**What:** A PostgreSQL driver for Python built specifically for async I/O (used internally by SQLAlchemy's async engine via the `postgresql+asyncpg://` URL scheme).
**Why:** The default `psycopg2` driver most tutorials use is sync-only. `asyncpg` is what actually makes async queries possible.

## FastAPI Dependency Injection (`Depends`)

**What:** FastAPI's mechanism for declaring "this route needs X" and having FastAPI provide it automatically — here, `Depends(get_db)` gives the route a DB session.
**Why:** Centralizes session creation/cleanup in one place (`get_db`), rather than every route manually opening and closing sessions. It also makes testing easier later — you can swap in a fake DB session for tests without touching route code.

## `expire_on_commit=False`

**What:** A session setting that stops SQLAlchemy from invalidating (expiring) Python objects after a commit.
**Why:** By default, after `commit()`, accessing an object's attributes triggers a fresh DB query. In an async context this can cause subtle bugs/extra queries. Disabling it means the object keeps its last-known values in memory after commit — the tradeoff being you must re-fetch manually if you need guaranteed-fresh data.

## Alembic

**What:** SQLAlchemy's official migration tool — tracks schema changes as an ordered sequence of versioned Python scripts.
**Why:** Letting SQLAlchemy auto-create tables (`Base.metadata.create_all()`) works for toy scripts but gives you no history, no rollback, and no safe way to evolve a schema that already has data in it. Alembic solves all three: every schema change is a reviewable, revertible migration file.
**When it matters:** Any time a model changes (new column, new table, renamed field) in this project, it goes through `alembic revision --autogenerate` + review + `alembic upgrade head` — never manual `ALTER TABLE` or `create_all()`.

## DeclarativeBase / shared Base class

**What:** The common parent class (`Base`) that all SQLAlchemy ORM models inherit from.
**Why:** SQLAlchemy uses `Base.metadata` to know about every table that exists. Alembic reads this same metadata to autogenerate migrations by diffing it against the actual DB schema. One shared `Base` = one source of truth for "what tables should exist."

## UUID primary keys vs auto-increment integers

**What:** Using a randomly generated UUID as a row's primary key instead of a sequential integer.
**Why:** Sequential IDs leak information (row counts, creation order) and can collide if you ever merge data from multiple databases (e.g. multi-tenant, migrations, sharding). UUIDs avoid both problems at the cost of slightly larger index size — a good tradeoff for user-facing entities.

## Enum columns

**What:** A database column constrained to a fixed set of string values (here, `UserRole.ADMIN` / `UserRole.END_USER`), backed by Python's `enum.Enum` and mapped via `sqlalchemy.Enum`.
**Why:** Enforces valid roles at the database level, not just in application code — a bad value can't sneak into `role` even from raw SQL or a bug elsewhere.

## bcrypt password hashing

**What:** A one-way hashing algorithm purpose-built for passwords, with a deliberately slow, tunable cost factor and a randomly generated salt baked into every hash it produces.
**Why:** Passwords must never be stored in plaintext or with reversible encryption — if the DB ever leaks, hashed passwords (properly salted) are extremely expensive to crack, whereas plaintext or weakly-hashed (e.g. plain MD5/SHA256) passwords are not. bcrypt's slowness is a _feature_ — it makes brute-forcing infeasible at scale.
**When it matters:** Every password anywhere in this system — user login, any future service credentials stored in the DB — goes through this, never raw.

## Why passlib was avoided

**What:** `passlib` is a popular older password-hashing wrapper library, but it's effectively unmaintained and has known compatibility breaks with recent `bcrypt` releases.
**Why:** Calling `bcrypt` directly avoids depending on an unmaintained middle layer for something as security-critical as password hashing.

## Unit tests vs integration tests (first look)

**What:** `test_security.py` is a **unit test** — it tests one function in isolation, with no database, no network, no external state.
**Why:** Unit tests should be the fastest, most numerous tests in the suite. Later, when we test things like "can a user log in via the API," those become **integration tests** (touching the DB, the HTTP layer) — slower, fewer, but catching different classes of bugs. Keeping this distinction clear now avoids a slow, tangled test suite later.

## One-off scripts vs API endpoints

**What:** `scripts/create_user.py` creates a user by calling the DB layer directly, bypassing the API entirely.
**Why:** Useful for seeding/admin tasks and, right now, for proving the model + security layer work before building the API surface on top. Not a substitute for real endpoints — Step 8 builds the actual `/auth/register` and `/auth/login` routes.

## JWT (JSON Web Token)

**What:** A signed, self-contained token encoding claims (here: user id, role, expiry) that the server can verify without a database lookup, just by checking the signature.
**Why:** Stateless auth — the server doesn't need to store sessions. The token itself proves identity as long as the signature (using `JWT_SECRET_KEY`) checks out and it hasn't expired.
**Caveat to remember:** Because JWTs are stateless, you can't easily "revoke" one before it expires (no server-side session to delete). For now our 60-minute expiry limits the blast radius; proper revocation (e.g. a blocklist, refresh-token rotation) is a later hardening step, not Phase 0.

## OAuth2PasswordBearer

**What:** FastAPI's built-in helper that reads the `Authorization: Bearer <token>` header from a request and extracts the raw token string.
**Why:** It's _only_ used here for the token extraction convenience and for `/docs`' "Authorize" button integration — we're not doing full OAuth2, just borrowing this one utility for bearer-token auth.

## FastAPI `APIRouter`

**What:** A way to group related routes (here, all `/auth/*` routes) into their own module, then mount them onto the main `app` via `include_router`.
**Why:** Keeps `main.py` from becoming a dumping ground for every route in the system. Each domain (auth, documents, chat, etc.) gets its own router file under `app/api/`.

## Dependency-based RBAC (`require_admin`)

**What:** A FastAPI dependency that wraps `get_current_user` and additionally checks the user's role, raising 403 if it doesn't match.
**Why:** This is the pattern the whole authorization system builds on: any route that needs restricting just adds `Depends(require_admin)` (or a future `require_role(...)` variant) to its signature. Authorization logic lives in one place, not copy-pasted into every route.

## `response_model` in FastAPI

**What:** Declaring `response_model=UserResponse` on a route tells FastAPI to serialize the return value through that Pydantic schema, filtering out any fields not defined on it.
**Why:** Critically, this is what keeps `hashed_password` out of API responses — even though the route returns a full `User` ORM object, only the fields on `UserResponse` (id, email, role, is_active) ever reach the client.

## In-process ASGI testing (`httpx.ASGITransport`)

**What:** A way to test a FastAPI app by talking to it directly in-process via its ASGI interface, with no real network socket or running `uvicorn` server involved.
**Why:** Much faster than spinning up a real server for tests, and avoids port-conflict flakiness. This is the standard way to integration-test FastAPI apps.

## Integration tests vs unit tests (in practice now)

**What:** `test_auth.py` tests exercise the real route → real dependency injection → real database, end to end. Contrast with `test_security.py` from Step 7, which tested one function in total isolation.
**Why:** Unit tests catch logic bugs fast and cheap; integration tests catch wiring bugs (wrong dependency, wrong status code, serialization leaking a field) that unit tests structurally can't see. Both are needed — neither is a substitute for the other.

## Test database isolation (why we're deferring it, not skipping it)

**What:** Right now our integration tests write real rows into the dev Postgres database. Proper practice is either a dedicated test database, or wrapping each test in a transaction that's rolled back afterward so tests never leave residue.
**Why it's deferred for now:** Solving this properly (test containers, fixtures with rollback) is its own small project. Doing it now would have doubled the size of this step for a Phase-0-skeleton project. Logged explicitly as debt so it doesn't get forgotten — this is a discipline worth practicing: acceptable shortcuts get written down, not silently ignored.

## Why we track "known debt" explicitly in the README

**What:** A dedicated section listing deliberate shortcuts taken and what's missing as a result.
**Why:** In real engineering, every non-trivial system has known gaps. Writing them down (rather than pretending the phase is "fully done") is what separates an honest, maintainable project from one where problems get discovered the hard way later.
