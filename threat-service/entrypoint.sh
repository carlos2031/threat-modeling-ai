#!/usr/bin/env bash

set -euo pipefail

# Garante que /app/uploads existe e é gravável pelo appuser (volume montado)
mkdir -p /app/uploads
chown -R appuser:appgroup /app/uploads 2>/dev/null || true

cli_help() {
  cli_name=${0##*/}
  echo "
$cli_name — Threat Modeling AI (threat-service)
Usage: $cli_name [command]

Commands:
  runserver   Start FastAPI server (default)
  test        Run tests with coverage
  health      Check health (curl /health)
  *           This help

Environment:
  PORT        Server port (default: 8000)
"
  exit 1
}

case "${1:-runserver}" in
  runserver)
    PORT=${PORT:-8000}
    echo "Starting threat-service on port $PORT..."
    exec runuser -u appuser -- uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
    ;;
  test)
    exec runuser -u appuser -- pytest tests/ -v --tb=short --cov=app --cov-report=term-missing --cov-config=.coveragerc
    ;;
  health)
    curl -sf "http://localhost:${PORT:-8000}/health" || exit 1
    exit 0
    ;;
  *)
    cli_help
    ;;
esac
