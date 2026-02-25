# threat-analyzer

Microserviço de análise de ameaças em diagramas de arquitetura. Recebe uma imagem via HTTP, executa o pipeline LLM (Diagram → STRIDE → DREAD) e retorna componentes, conexões, ameaças e scores em JSON. Parte do projeto [Threat Modeling AI](../README.md).

## O que faz

- **Endpoint principal:** `POST /api/v1/threat-model/analyze` (multipart: imagem do diagrama).
- **Pipeline:** Guardrail (validação de diagrama de arquitetura) → DiagramAgent (extração de componentes/conexões) → StrideAgent (ameaças STRIDE com RAG) → DreadAgent (pontuação DREAD).
- **Fallback LLM:** Gemini → OpenAI → Ollama (sequencial).
- **Health:** `GET /`, `/health`, `/health/ready`, `/health/live`.

Não persiste estado; é chamado pelo orquestrador (threat-service) via Celery worker.

## Stack

| Tecnologia                                                 | Uso                                     |
| ---------------------------------------------------------- | --------------------------------------- |
| Python 3.11+                                               | Runtime                                 |
| FastAPI                                                    | API REST                                |
| LangChain                                                  | Orquestração LLM                        |
| langchain-google-genai, langchain-openai, langchain-ollama | Provedores LLM                          |
| ChromaDB (langchain-community)                             | RAG (base de conhecimento STRIDE/DREAD) |
| Pydantic                                                   | Config e schemas                        |
| threat-modeling-shared                                     | Health, config base, middleware         |

## Requisitos

- Python 3.10+
- Dependência local: `threat-modeling-shared` (path `../threat-modeling-shared` em desenvolvimento; no Docker o build do projeto raiz deve resolver).

## Instalação

### Local (desenvolvimento)

Na raiz do repositório:

```bash
# Criar venv e instalar dependências do backend (inclui threat-analyzer e threat-service)
make setup-backend
```

Ou apenas para este serviço:

```bash
cd threat-analyzer
pip install -e ../threat-modeling-shared
pip install -r requirements.txt
# Para rodar testes localmente:
pip install -r requirements-test.txt
```

### Docker (multi-stage: base → test → runtime)

O Dockerfile tem três estágios: **base** (deps + app, sem testes), **test** (deps de teste + `tests/`, usado em CI) e **runtime** (imagem final, sem testes nem pytest). A imagem de produção é só o estágio `runtime`.

O build deve ser feito **a partir da raiz do repositório** para incluir `threat-modeling-shared`:

```bash
# Na raiz do projeto
docker compose up -d --build threat-analyzer
```

Ou apenas build da imagem:

```bash
make -C threat-analyzer build   # imagem runtime
make -C threat-analyzer test-image   # build stage test e roda pytest (CI)
```

Porta exposta: **8001** (host) → 8000 (container). O orquestrador usa `ANALYZER_URL` (ex.: `http://threat-analyzer:8000`) para chamar o analyzer.

## Configuração

Variáveis de ambiente (via `configs/.env` no Docker ou ambiente local). O serviço herda de `threat_modeling_shared.config.BaseSettings` e adiciona:

| Variável              | Descrição                          | Default                                         |
| --------------------- | ---------------------------------- | ----------------------------------------------- |
| `GOOGLE_API_KEY`      | Chave da API Google (Gemini)       | —                                               |
| `OPENAI_API_KEY`      | Chave da API OpenAI                | —                                               |
| `OLLAMA_BASE_URL`     | URL do Ollama (LLM local)          | `http://localhost:11434`                        |
| `OLLAMA_MODEL`        | Modelo vision Ollama               | `qwen2-vl`                                      |
| `USE_DUMMY_PIPELINE`  | `true` para testes (resposta fixa) | `false`                                         |
| `KNOWLEDGE_BASE_PATH` | Pasta da base RAG (opcional)       | `app/rag_data` (container: `/app/app/rag_data`) |

Tipos de imagem permitidos: `image/jpeg`, `image/png`, `image/webp`, `image/gif`. Tamanho máximo configurável via settings (default 10 MB).

## Base RAG (dados para STRIDE/DREAD)

O pipeline STRIDE usa uma base de conhecimento (RAG) para enriquecer as respostas. A pasta fica **dentro da app**: `app/rag_data/` (no container: `/app/app/rag_data`).

- **Repositório:** A pasta `app/rag_data/` é versionada com `.gitkeep`; o **conteúdo** (arquivos .md da base) não é commitado.
- **Como preencher:** Coloque os arquivos .md da base (stride/ e dread/) em `app/rag_data/`. O conteúdo não é versionado; a pasta tem `.gitkeep`. Quem tiver o contexto privado (`private-context/notebooks/`) pode usar os scripts de processamento RAG que estavam nos notebooks (agora fora do repositório).
- Opcional: variável `KNOWLEDGE_BASE_PATH` para sobrescrever o path. Se a pasta não existir ou estiver vazia, o RAG não é carregado (path retorna `None` no config).

## Execução

### Servidor (local)

```bash
cd threat-analyzer
PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Ou via entrypoint (Docker ou local):

```bash
./entrypoint.sh runserver
```

### Comandos do entrypoint

| Comando     | Descrição                                       |
| ----------- | ----------------------------------------------- |
| `runserver` | Sobe o servidor FastAPI (porta 8000 ou `$PORT`) |
| `test`      | Roda testes com pytest/coverage                 |

## Estrutura do projeto

```
threat-analyzer/
├── app/
│   ├── main.py              # FastAPI app, registro de rotas
│   ├── core/                 # Config, logging, dependencies
│   └── threat_analysis/      # Pipeline de análise
│       ├── router.py         # POST /analyze
│       ├── controllers/      # Orquestração da requisição
│       ├── agents/           # Diagram, Stride, Dread
│       ├── llm/              # Fallback, cache, conexões
│       ├── guardrails/       # Validação de diagrama
│       └── schemas/          # Request/response
├── tests/                    # Espelha app/
├── Dockerfile
├── entrypoint.sh
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Testes e lint

- **Local:** na raiz do repositório, com venv que tenha `threat-modeling-shared` e deps instaladas:  
  `make -C threat-analyzer test` (pytest + coverage) e `make -C threat-analyzer lint` (ruff).
- **CI:** build do estágio `test` e execução no container:  
  `make -C threat-analyzer test-image` (build da imagem de test e `docker run` com pytest). Testes e libs de teste não entram na imagem final (`runtime`).

## API (resumo)

- **POST /api/v1/threat-model/analyze** — Body: `multipart/form-data` com `file` (imagem obrigatória); opcionais: `confidence`, `iou`. Resposta 200: JSON com `model_used`, `components`, `connections`, `threats`, `risk_score`, `risk_level`, `processing_time`, etc. Erros: 400 (tipo inválido ou guardrail), 500 (erro interno).
- **GET /health**, **GET /health/ready**, **GET /health/live** — Health checks (shared).

Documentação completa: [docs/specs/20-design/api-contracts.md](../docs/specs/20-design/api-contracts.md) e [docs/Postman Collections/](../docs/Postman%20Collections/).
