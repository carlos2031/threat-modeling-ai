# threat-service — build, test, lint (padrão: camadas Docker; testes fora do runtime)
# Build da imagem final: make build (ou na raiz: make build-service)
# Testes em CI: make test-image (build stage test e roda pytest)
ROOT := $(shell cd .. && pwd)
PYTHON := $(if $(wildcard $(ROOT)/.venv/bin/python),$(ROOT)/.venv/bin/python,python3)

# Docker (build from repo root so threat-modeling-shared is available)
IMAGE_NAME ?= threat-modeling-ai-threat-service
TAG ?= latest
DOCKERFILE := $(CURDIR)/Dockerfile
CONTEXT ?= $(ROOT)

.PHONY: help build build-test test-image run test lint clean

help: ## Listar comandos
	@echo "Comandos:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

## Docker
build: ## Build imagem runtime (stage runtime)
	cd $(CONTEXT) && docker build -f threat-service/Dockerfile --target runtime -t $(IMAGE_NAME):$(TAG) .

build-test: ## Build stage test (para CI)
	cd $(CONTEXT) && docker build -f threat-service/Dockerfile --target test -t $(IMAGE_NAME)-test:$(TAG) .

test-image: build-test ## Rodar testes dentro do container (CI)
	docker run --rm $(IMAGE_NAME)-test:$(TAG)

run: build ## Rodar container (porta 8000)
	docker run --rm -p 8000:8000 $(IMAGE_NAME):$(TAG)

## Local (venv na raiz ou sistema)
test: ## Testes locais (PYTHONPATH e shared no venv da raiz)
	cd $(ROOT) && PYTHONPATH=threat-service:threat-modeling-shared $(PYTHON) -m pytest threat-service/tests/ \
		--cov=app --cov-report=term-missing --cov-config=threat-service/.coveragerc -v --tb=short

lint: ## Ruff check + format
	ruff check . --fix
	ruff format .

clean: ## Remover caches
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
