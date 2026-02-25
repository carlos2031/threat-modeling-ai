.DEFAULT_GOAL := help

# =============================================================================
# Threat Modeling AI - Makefile
# =============================================================================

PROJECT_ROOT := $(dir $(abspath $(firstword $(MAKEFILE_LIST))))
COMPOSE_ENV := $(PROJECT_ROOT)configs/.env
PYTHON := $(if $(wildcard $(PROJECT_ROOT).venv/bin/python),$(PROJECT_ROOT).venv/bin/python,python3)

help:
	@echo "=============================================="
	@echo "  Threat Modeling AI - Comandos Disponiveis"
	@echo "=============================================="
	@echo ""
	@echo "SETUP / INSTALACAO:"
	@echo "  make setup              - Setup completo (backend + frontend)"
	@echo "  make setup-backend      - So backend (.venv)"
	@echo "  make setup-frontend     - So frontend (npm install)"
	@echo "  make install-local-llm  - Sobe Ollama, baixa modelos vision e verifica (um comando)"
	@echo ""
	@echo "RUN (Docker):"
	@echo "  make run                - Sobe a aplicacao com logs no terminal"
	@echo "  make run-detached       - Sobe a aplicacao em background (producao)"
	@echo ""
	@echo "TESTES UNITARIOS:"
	@echo "  make test                - Roda testes do threat-analyzer e do threat-service"
	@echo "  make test-analyzer       - So threat-analyzer"
	@echo "  make test-service        - So threat-service"
	@echo ""
	@echo "TESTE DE FLUXO (stack rodando, ex.: make run):"
	@echo "  make test-analysis-flow IMAGE=caminho/para/diagrama.png - Envia imagem ao threat-analyzer e exibe resposta"
	@echo ""

# -----------------------------------------------------------------------------
# SETUP / INSTALACAO
# -----------------------------------------------------------------------------

setup: setup-backend setup-frontend
	@echo "Setup completo."

setup-backend:
	@echo "==> Setup backend (threat-analyzer + threat-service)..."
	@if [ ! -d .venv ]; then python3 -m venv .venv && .venv/bin/pip install --upgrade pip -q; fi
	.venv/bin/pip install -r threat-analyzer/requirements.txt -q
	.venv/bin/pip install -r threat-service/requirements.txt -q
	@echo "Backend instalado em .venv/"

setup-frontend:
	@echo "==> Instalando dependencias do threat-frontend..."
	cd threat-frontend && npm install
	@echo "threat-frontend instalado."

install-local-llm:
	@chmod +x scripts/install_local_llm.sh
	@./scripts/install_local_llm.sh

# -----------------------------------------------------------------------------
# RUN
# -----------------------------------------------------------------------------

run:
	cd $(PROJECT_ROOT) && docker compose --env-file $(COMPOSE_ENV) up --build

run-detached:
	cd $(PROJECT_ROOT) && docker compose --env-file $(COMPOSE_ENV) up --build -d

test: test-analyzer test-service
	@echo "Todos os testes passaram."

test-analyzer:
	@echo "==> Testes threat-analyzer..."
	$(MAKE) -C threat-analyzer test

test-service:
	@echo "==> Testes threat-service..."
	$(MAKE) -C threat-service test

test-analysis-flow:
	@echo "==> Fluxo de teste de analise (threat-analyzer em http://localhost:8002 com Docker)..."
	@if [ -z "$(IMAGE)" ]; then echo "Passe IMAGE=caminho/para/diagrama.png"; exit 1; fi
	PYTHONPATH=$(PROJECT_ROOT) $(PYTHON) scripts/run_analysis_flow.py --base-url http://localhost:8002 --image $(IMAGE)

.PHONY: help setup setup-backend setup-frontend install-local-llm run run-detached test test-analyzer test-service test-analysis-flow
