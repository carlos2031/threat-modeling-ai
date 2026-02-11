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
	@echo "  make setup              - Setup completo (backend + frontend + notebooks)"
	@echo "  make setup-backend      - So backend (.venv)"
	@echo "  make setup-frontend     - So frontend (npm install)"
	@echo "  make setup-notebooks    - So notebooks (kernel Jupyter)"
	@echo "  make install-local-llm  - Sobe Ollama, baixa modelos vision e verifica (um comando)"
	@echo ""
	@echo "DATASETS (um comando por base: download + verificacao + conversao):"
	@echo "  make download-roboflow  - Prepara base Roboflow (requer ROBOFLOW_API_KEY)"
	@echo "  make download-kaggle    - Prepara base Kaggle (requer kaggle CLI ou ZIP)"
	@echo ""
	@echo "RAG:"
	@echo "  make process-rag-kb     - Processar input_files, gera output e arquivo unico comprimido"
	@echo ""
	@echo "TREINAMENTO (notebooks):"
	@echo "  make train-roboflow     - Treinar YOLO no dataset Roboflow"
	@echo "  make train-kaggle       - Treinar YOLO no dataset Kaggle"
	@echo ""
	@echo "RUN (apenas docker):"
	@echo "  make run                - Sobe a aplicacao com logs no terminal"
	@echo "  make run-detached       - Sobe a aplicacao em background (producao)"
	@echo ""
	@echo "TESTE DE FLUXO (API deve estar rodando, ex.: make run):"
	@echo "  make test-analysis-flow - Envia imagens de teste ao threat-analyzer e exibe resposta"
	@echo ""

# -----------------------------------------------------------------------------
# SETUP / INSTALACAO
# -----------------------------------------------------------------------------

setup: setup-backend setup-frontend setup-notebooks
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

setup-notebooks:
	@echo "==> Setup notebooks (libs + kernel Jupyter)..."
	./notebooks/scripts/setup_venv_kernel.sh
	@echo "Notebooks prontos. Kernel: Python (threat-modeling-ai)"

install-local-llm:
	@chmod +x scripts/install_local_llm.sh
	@./scripts/install_local_llm.sh

# -----------------------------------------------------------------------------
# DATASETS
# -----------------------------------------------------------------------------

download-roboflow:
	@echo "==> Preparando base Roboflow (download + verificacao)..."
	PYTHONPATH=. $(PYTHON) -m notebooks.scripts.download.prepare_roboflow

download-kaggle:
	@echo "==> Preparando base Kaggle (download + conversao + verificacao)..."
	PYTHONPATH=. $(PYTHON) -m notebooks.scripts.download.prepare_kaggle

# -----------------------------------------------------------------------------
# RAG (Knowledge Base)
# -----------------------------------------------------------------------------

process-rag-kb:
	@echo "==> Processando base RAG (input_files -> output_files + arquivo comprimido)..."
	PYTHONPATH=. $(PYTHON) -m notebooks.scripts.rag_processing.process_knowledge_base
	@echo "Saida em notebooks/knowledge-base/output_files/"

# -----------------------------------------------------------------------------
# TREINAMENTO (notebooks - YOLO 11)
# -----------------------------------------------------------------------------

train-roboflow:
	@echo "==> Treinando YOLO no dataset Roboflow..."
	PYTHONPATH=. $(PYTHON) -m notebooks.scripts.train.train_yolo --dataset roboflow

train-kaggle:
	@echo "==> Treinando YOLO no dataset Kaggle..."
	PYTHONPATH=. $(PYTHON) -m notebooks.scripts.train.train_yolo --dataset kaggle

# -----------------------------------------------------------------------------
# RUN
# -----------------------------------------------------------------------------

run:
	cd $(PROJECT_ROOT) && docker compose --env-file $(COMPOSE_ENV) up --build

run-detached:
	cd $(PROJECT_ROOT) && docker compose --env-file $(COMPOSE_ENV) up --build -d

# Requer threat-analyzer rodando (ex.: make run em outro terminal). Opcional: make process-rag-kb antes.
test-analysis-flow:
	@echo "==> Fluxo de teste de analise (imagens em notebooks/assets/)..."
	PYTHONPATH=$(PROJECT_ROOT) $(PYTHON) scripts/run_analysis_flow.py --base-url http://localhost:8001

.PHONY: help setup setup-backend setup-frontend setup-notebooks install-local-llm \
        download-roboflow download-kaggle process-rag-kb train-roboflow train-kaggle \
        run run-detached test-analysis-flow
