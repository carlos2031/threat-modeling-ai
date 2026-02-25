# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2025-02-23

### Added

- **Automated threat analysis** of cloud architecture diagrams using multimodal LLMs (Gemini, OpenAI, or Ollama with automatic fallback).
- **STRIDE methodology**: threat identification per component and connection (Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege).
- **DREAD scoring**: per-threat scores for Damage, Reproducibility, Exploitability, Affected users, and Discoverability; aggregate risk score (0–10) and risk level (LOW, MEDIUM, HIGH, CRITICAL).
- **Pipeline**: Guardrail (architecture-diagram validation) → DiagramAgent (components, connections, trust boundaries) → StrideAgent (STRIDE threats, optional RAG) → DreadAgent (DREAD scores).
- **Upload** of architecture diagrams (PNG, JPEG, WebP, GIF) via REST API and web UI.
- **Asynchronous analysis** with background processing (Celery); results persisted in PostgreSQL.
- **Real-time notifications** when analyses complete.
- **Analyses list** with filters, thumbnails, and delete-with-confirmation.
- **RAG (ChromaDB)** for STRIDE context and mitigation suggestions.
- **REST API** (FastAPI): threat-service orchestrator (port 8000), threat-analyzer pipeline (port 8002); OpenAPI and Postman collections.
- **Web frontend** (React, Vite, Tailwind, Framer Motion): dark theme, responsive layout, upload with preview, analysis detail view.
- **Docker Compose** stack: frontend, threat-service, threat-analyzer, PostgreSQL, Redis, Celery worker and beat.
