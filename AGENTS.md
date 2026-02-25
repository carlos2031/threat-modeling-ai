# AGENTS.md

## Cursor Cloud specific instructions

### Overview

Threat Modeling AI is a full-stack system for automated threat analysis of architecture diagrams. It consists of:

| Service | Tech | Dev Port | Description |
|---------|------|----------|-------------|
| **threat-analyzer** | FastAPI | 8002 (Docker) | STRIDE/DREAD analysis engine with LLM fallback chain |
| **threat-service** | FastAPI + Celery | 8000 (Docker) | API orchestrator — upload, async processing, DB |
| **threat-frontend** | React/Vite | 5173 (local dev) | SPA for diagram upload and analysis viewing |
| **Database** | 15-alpine | 5432 | Primary relational database |
| **Redis** | 7-alpine | 6379 | Celery broker/backend |
| **celery-worker** | Same image as threat-service | — | Processes analysis tasks |
| **celery-beat** | Same image as threat-service | — | Periodic scheduler (scans pending analyses every 60s) |

### Running the stack

Standard commands are documented in the root `README.md` and `Makefile`. Key non-obvious caveats:

- **Docker is required.** Backend services run via `docker compose --env-file configs/.env up -d [REDACTED] redis threat-analyzer threat-service celery-worker celery-beat`. The frontend Docker build has pre-existing TypeScript errors; run the frontend locally instead with `cd threat-frontend && npx vite --host 0.0.0.0`.
- **`configs/.env`**: Copy from `configs/.env.example`. Set `USE_DUMMY_PIPELINE=true` for development without LLM API keys (Gemini/OpenAI). The dummy pipeline returns placeholder analysis results.
- **Permission gotchas with Docker volume mounts:**
  - `threat-service/entrypoint.sh` must have execute permission on the host (`chmod +x threat-service/entrypoint.sh`), because the Docker Compose volume mount `./threat-service:/app` overrides the container filesystem.
  - `threat-service/media/` directory must exist and be writable (`mkdir -p threat-service/media && chmod 777 threat-service/media`) — the `appuser` inside the container cannot create it.
  - `threat-service/` directory must be writable for celery-beat's schedule file (`chmod 777 threat-service/`).

### Lint

- **Python**: `ruff check <dir>` — config is in each service's `pyproject.toml`. Pre-existing lint warnings exist.
- **Frontend**: ESLint is configured in `package.json` scripts but has no `.eslintrc` config file and `eslint` is not a devDependency. The `npm run lint` command will fail. TypeScript checking via `npx tsc --noEmit` also shows pre-existing errors.

### Tests

- **threat-analyzer**: `cd /workspace && PYTHONPATH=threat-analyzer:threat-modeling-shared .venv/bin/python -m pytest threat-analyzer/tests/ -v` — 103 pass, 2 skip (Redis tests skipped without Redis).
- **threat-service**: `cd /workspace && PYTHONPATH=threat-service:threat-modeling-shared .venv/bin/python -m pytest threat-service/tests/ --ignore=threat-service/tests/test_main.py -v` — 51 pass, 2 skip, some pre-existing failures/errors (stale test mocks referencing removed attributes like `_db_check`, `get_db`, `httpx`). Integration tests skip without a dedicated test database.

### Frontend dev server

Run `cd threat-frontend && npx vite --host 0.0.0.0 --port 5173` for HMR development. The Vite config proxies `/api` requests to `http://localhost:8000` (threat-service).

### Shared library

`threat-modeling-shared` is installed in editable mode (`pip install -e threat-modeling-shared`). Changes to it are picked up immediately by the backend services in the local venv, but Docker containers need a rebuild.
