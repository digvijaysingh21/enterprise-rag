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
