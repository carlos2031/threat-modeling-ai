# threat-analyzer — multi-stage: base (deps + app), test (CI), runtime (final)
# Build from repo root: docker build -f threat-analyzer/Dockerfile .
# Compose: context: .  dockerfile: threat-analyzer/Dockerfile

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
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Shared lib (build context = repo root)
COPY threat-modeling-shared /tmp/threat-modeling-shared
RUN pip install --no-cache-dir /tmp/threat-modeling-shared

COPY threat-analyzer/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY threat-analyzer/app ./app
COPY threat-analyzer/entrypoint.sh .
COPY threat-analyzer/pyproject.toml .
RUN chmod +x ./entrypoint.sh

EXPOSE 8000

# -----------------------------------------------------------------------------
# Stage: test — CI only; tests + test deps (not in final image)
# -----------------------------------------------------------------------------
FROM base AS test

COPY threat-analyzer/requirements-test.txt .
RUN pip install --no-cache-dir -r requirements-test.txt

COPY threat-analyzer/tests ./tests
COPY threat-analyzer/.coveragerc .

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["test"]

# -----------------------------------------------------------------------------
# Stage: runtime — final image (no tests, no pytest)
# -----------------------------------------------------------------------------
FROM base AS runtime

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser \
    && chown -R appuser:appgroup /app \
    && chmod +x /app/entrypoint.sh
USER appuser

LABEL org.opencontainers.image.title="threat-analyzer" \
      org.opencontainers.image.description="Threat analysis service (STRIDE, DREAD, LLM)" \
      org.opencontainers.image.vendor="Threat Modeling AI"

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["runserver"]
