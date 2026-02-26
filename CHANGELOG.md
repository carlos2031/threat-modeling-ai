# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Threat deduplication: only one entry per (threat_type, normalized description) in analysis results; duplicate STRIDE threats from the LLM are dropped.
- Script `scripts/clear_and_run_test_analyses.py`: clears all analyses via threat-service API and runs analyses for `test-assets/diagrama-aws.png` and `test-assets/diagrama-azure.png`.

### Changed

- Deploy instructions moved to private context (cursor-multiagent-system `config/cicd/projects/threat-modeling-ai.md`); `docs/DEPLOY_VPS.md` removed from repo.

### Fixed

- Duplicate vulnerabilities (e.g. repeated "Information Disclosure") no longer appear multiple times in the analyses list; each distinct threat type + description is stored once.

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
