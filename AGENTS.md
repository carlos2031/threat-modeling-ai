# AGENTS.md

## Cursor Cloud specific instructions

### Overview

Threat Modeling AI is a multi-service application for automated threat analysis of architecture diagrams. See `README.md` for full documentation.

### Services

| Service | Port | Notes |
|---|---|---|
| PG 15 (database) | 5432 | Primary DB for threat-service |
| Redis 7 | 6379 | Celery broker + cache |
| threat-analyzer (FastAPI) | 8002→8000 | STRIDE/DREAD analysis engine |
| threat-service (FastAPI) | 8000 | Orchestrator API |
| celery-worker | — | Async task processor |
| celery-beat | — | Periodic task scheduler |
| threat-frontend (React/Vite) | 5173 (dev) | Upload diagrams, view analyses |

### Running the stack

Backend services run via Docker Compose (from repo root):
```bash
cp configs/.env.example configs/.env  # if not already done
chmod +x threat-service/entrypoint.sh threat-frontend/entrypoint.sh
mkdir -p threat-service/media && chmod 777 threat-service/media
sudo docker compose --env-file configs/.env up -d [REDACTED] redis threat-analyzer threat-service celery-worker celery-beat
```

Frontend dev server (runs separately, not via Docker):
```bash
cd threat-frontend && npx vite --host 0.0.0.0 --port 5173
```

**Important gotchas:**
- `threat-service/entrypoint.sh` lacks execute permission in git. You must `chmod +x` it before Docker Compose can start the container (the volume mount overrides the Dockerfile's `chmod`).
- The `threat-service` container needs a writable `media/` directory: `mkdir -p threat-service/media && chmod 777 threat-service/media`.
- The frontend Docker image (`npm run build` = `tsc && vite build`) fails due to pre-existing TypeScript errors. Run the frontend in dev mode (`npx vite`) instead, which bypasses TS checking.
- `celery-beat` may fail with `Permission denied: 'celerybeat-schedule'` due to volume mount permissions. If so, `touch threat-service/celerybeat-schedule && chmod 666 threat-service/celerybeat-schedule` and restart.
- Without LLM API keys (`GOOGLE_API_KEY`, `OPENAI_API_KEY`, or Ollama), threat-analyzer returns fallback results. This is fine for environment validation.
- Docker must be started manually in Cloud Agent VMs: `sudo dockerd &>/tmp/dockerd.log &` (no systemd).

### Lint and test

See per-service Makefiles for commands. From repo root with venv active:
```bash
# Lint (Python)
.venv/bin/ruff check threat-modeling-shared/ threat-analyzer/ threat-service/

# Tests
PYTHONPATH=threat-analyzer:threat-modeling-shared .venv/bin/python -m pytest threat-analyzer/tests/ -v --tb=short
PYTHONPATH=threat-service:threat-modeling-shared .venv/bin/python -m pytest threat-service/tests/ -v --tb=short --ignore=threat-service/tests/test_main.py
```

**Pre-existing test issues in threat-service:**
- `tests/test_main.py`: imports `_db_check` which doesn't exist in `app.main` — skip with `--ignore`.
- Several router tests fail with `AttributeError: 'module' object at app.main has no attribute 'get_db'`.
- `test_analysis_processing_service.py`: some tests reference `httpx` attribute that no longer exists in the service module.
- `test_config.py::test_settings_defaults`: expects `upload_dir == 'uploads'` but config now uses `'media'`.

### Frontend lint

ESLint is referenced in `package.json` scripts but no config file (`.eslintrc*` or `eslint.config.*`) exists and `eslint` is not a devDependency. Frontend lint is non-functional until this is set up.

### Analysis pipeline

The analyses list API returns a paginated response (`{ items, total, page, size, pages }` via `fastapi-pagination`). The frontend's `listAnalyses` function must extract the `items` array.

The full analysis flow is: upload → `EM_ABERTO` → celery-beat triggers `scan_pending_analyses` every minute → marks `PROCESSANDO` → celery-worker calls threat-analyzer → marks `ANALISADO` → creates notification. To manually trigger processing: `sudo docker exec workspace-celery-worker-1 celery -A app.celery_app call app.analysis.tasks.analysis_tasks.scan_pending_analyses`.
