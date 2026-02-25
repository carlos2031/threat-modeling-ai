# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Runbook `roteiro-apresentacao-10min.md`: roteiro de apresentação em 10 min (fluxo, arquitetura, agentes).
- Alvos no Makefile raiz: `test`, `test-analyzer`, `test-service`; `test-analysis-flow` usando porta 8002 (Docker).

### Changed

- Docstrings e comentários (tom mais neutro): `threat_modeling_shared/cache.py`, `threat_analysis/agents/base.py`, `threat_analysis/schemas/response.py`.
- Frontend: ajustes em `UploadSection.tsx`, `AnalysesListPage.tsx` e `threatModelingService.ts`.
- `docker-compose.yml` e `assets/banner.svg` atualizados.
- `threat-service`: controller, repository e router de análise; Makefile com `PYTHONPATH` alinhado ao diretório `threat-service`.
- Runbooks: README da pasta 90-runbooks atualizado; remoção de referências a runbooks antigos.

### Removed

- Runbooks: `plano-validacao-hackaton.md`, `roteiro-apresentacao-prototipo1-prototipo2.md`, `auditoria-textos-ia.md`, `revisao-codigo-doc.md`.

### Fixed

- threat-service testes: `conftest.py` com `dependency_overrides` em vez de monkeypatch; `test_main.py` sem `_db_check`, lifespan com mocks; `test_config.py` assert de `upload_dir` para `Path("media")`; `test_analysis_processing_service.py` mocks com `is_done`/`is_failed`/`is_open` e patch de `httpx` no módulo correto.
- Docstring do pacote de testes do threat-service: referência a "threat-service" em vez de "threat-modeling-api".
