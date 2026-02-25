# threat-service — multi-stage: base (deps + app), test (CI), runtime (final)
# Build from repo root: docker build -f threat-service/Dockerfile .
# Compose: context: .  dockerfile: threat-service/Dockerfile

# -----------------------------------------------------------------------------
# Stage: base — runtime deps + app (no tests, no test libs)
# -----------------------------------------------------------------------------
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    util-linux \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Shared lib (build context = repo root)
COPY threat-modeling-shared /tmp/threat-modeling-shared
RUN pip install --no-cache-dir /tmp/threat-modeling-shared

COPY threat-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY threat-service/app ./app
COPY threat-service/entrypoint.sh .
COPY threat-service/pyproject.toml .
RUN chmod +x ./entrypoint.sh

EXPOSE 8000

# -----------------------------------------------------------------------------
# Stage: test — CI only; tests + test deps (not in final image)
# -----------------------------------------------------------------------------
FROM base AS test

COPY threat-service/requirements-test.txt .
RUN pip install --no-cache-dir -r requirements-test.txt

COPY threat-service/tests ./tests
COPY threat-service/.coveragerc .

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["test"]

# -----------------------------------------------------------------------------
# Stage: runtime — final image (no tests, no pytest)
# -----------------------------------------------------------------------------
FROM base AS runtime

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser \
    && chown -R appuser:appgroup /app
# Entrypoint roda como root para chown em /app/uploads (volume), depois runuser para appuser

LABEL org.opencontainers.image.title="threat-service" \
      org.opencontainers.image.description="Threat modeling API (orchestrator, Celery)" \
      org.opencontainers.image.vendor="Threat Modeling AI"

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["runserver"]
