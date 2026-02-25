# Documentação — Threat Modeling AI

Documentação central do projeto: explicação do sistema (fluxo, pipeline, agentes, LLM, guardrail) e referência às especificações (Spec Driven) e às coleções Postman.

---

## Índice

1. [Fluxo básico de análise](#1-fluxo-basico-de-analise)
2. [ThreatModelService (orquestração)](#2-threatmodelservice-orquestracao)
3. [Módulo LLM (fallback e cache)](#3-modulo-llm-fallback-e-cache)
4. [Agentes do pipeline](#4-agentes-do-pipeline)
5. [Guardrail (validação de diagrama)](#5-guardrail-validacao-de-diagrama)
6. [Specs e Postman](#6-specs-e-postman)

---

## 1. Fluxo básico de análise

### Objetivo

1. Subir a aplicação (stack via Docker).
2. Enviar imagens de diagramas para o endpoint `POST /api/v1/threat-model/analyze` do threat-analyzer e obter a resposta com componentes, conexões, ameaças STRIDE e pontuação DREAD.

### Pré-requisitos

- Python 3.10+ e dependências do projeto (`make setup-backend` na raiz) para testes locais.
- API rodando: `make run` sobe a stack; o threat-analyzer fica em `http://localhost:8002` (mapeado do 8000 no container).

### Subir a aplicação

Na raiz do projeto:

```bash
make run
```

Isso sobe todos os serviços via Docker Compose (frontend :80, threat-service :8000, threat-analyzer :8002, postgres, redis, celery-worker, celery-beat, ollama opcional). O health do threat-analyzer pode ser verificado em `http://localhost:8002/health/`.

### Testar o fluxo de análise

**Script (recomendado):** passe ao menos uma imagem com `IMAGE=`:

```bash
make test-analysis-flow IMAGE=caminho/para/diagrama.png
```

Ou chamando o script diretamente (uma ou mais imagens):

```bash
PYTHONPATH=. python scripts/run_analysis_flow.py --image diagrama.png --image outro.png
```

**Requisição com curl:** o endpoint é POST em multipart/form-data; o campo obrigatório é `file` (imagem):

```bash
curl -X POST http://localhost:8002/api/v1/threat-model/analyze -F "file=@diagrama.png"
```

**Tipos aceitos:** `image/png`, `image/jpeg`, `image/webp`, `image/gif`.

**Resposta (200 OK):** JSON com `model_used`, `components`, `connections`, `threats` (STRIDE + DREAD), `risk_score`, `risk_level`, `processing_time`.

**Erros comuns:**

- **400 — tipo de arquivo inválido:** arquivo que não é imagem (ex.: PDF).
- **400 — diagrama rejeitado pelo guardrail:** imagem não considerada diagrama de arquitetura.
- **500:** falha interna (LLM indisponível, configuração).

### Ordem recomendada para validar

1. Subir a stack: `make run`.
2. Aguardar health: `curl -s http://localhost:8002/health/` retorna 200.
3. Rodar o fluxo: `make test-analysis-flow IMAGE=caminho/para/diagrama.png`.

---

## 2. ThreatModelService (orquestração)

A classe **`ThreatModelService`** do threat-analyzer é o orquestrador do pipeline. Ela não implementa análise nem STRIDE/DREAD diretamente; delega a agentes especializados e coordena a ordem das etapas.

**Fluxo de chamada:**

```
Router (POST /analyze) → Controller → ThreatModelService.run_full_analysis() → AnalysisResponse
```

### Pipeline (visão de alto nível)

1. **Guardrail:** `validate_architecture_diagram(image_bytes)` — valida se a imagem é diagrama de arquitetura; rejeita fotos, diagramas de sequência, fluxogramas.
2. **Estágio 1 — Diagram:** `DiagramAgent.analyze(image_bytes)` — extrai componentes, conexões e trust boundaries.
3. **Estágio 2 — STRIDE:** `StrideAgent.analyze(diagram_data)` — identifica ameaças STRIDE por componente/conexão (com RAG opcional).
4. **Estágio 3 — DREAD:** `DreadAgent.analyze(threats)` — pontua cada ameaça (Damage, Reproducibility, Exploitability, Affected users, Discoverability).
5. **Agregação:** `_calculate_risk_score(scored_threats)` — risco global = média dos dread_score; `RiskLevel.from_score(score)` → LOW | MEDIUM | HIGH | CRITICAL.
6. **Resposta:** montagem de `AnalysisResponse` com `_parse_components`, `_parse_connections`, `_parse_threats` (parsers tolerantes a falha por item).

### Construtor e agentes (lazy loading)

Os agentes (`DiagramAgent`, `StrideAgent`, `DreadAgent`) são criados sob demanda (propriedades com lazy load). Assim, se a requisição falhar no guardrail ou no Diagram, STRIDE e DREAD nem são instanciados. O singleton `get_threat_model_service()` (lru_cache) mantém as mesmas instâncias entre requisições para cache e reuso.

### Pontos críticos

- **Parsers:** cada `_parse_*` usa try/except por item; em falha registra warning e não adiciona o item, evitando 500 por resposta malformada do LLM.
- **Risco:** lista vazia de ameaças → risk_score 0.0; ameaças sem dread_score contam como 0.

---

## 3. Módulo LLM (fallback e cache)

O módulo `app.threat_analysis.llm` oferece múltiplos provedores de LLM com fallback automático e cache.

### Objetivo

- **Visão (imagem):** extrair componentes e conexões do diagrama (Diagram Agent, guardrail).
- **Texto:** gerar análise STRIDE e pontuação DREAD.

Provedores podem falhar (não configurado, rate limit, timeout, resposta inválida). Por isso:

1. **Fallback em cadeia:** lista ordenada (ex.: Gemini → OpenAI → Ollama); tenta a próxima se a atual falhar ou não entregar resultado válido.
2. **Cache (Redis):** evita chamadas repetidas para o mesmo input; TTL 2 horas.
3. **Contrato único:** todas as conexões retornam dict (resultado ou `error` / `error_type` / `service`).

### Componentes

- **fallback.py:** `run_vision_with_fallback`, `run_text_with_fallback`; consulta cache → se hit e válido retorna; senão tenta cada conexão; `_validation_check(validator, result, conn_name)`.
- **cache.py:** `LLMCacheService` (Redis, TTL 2h, chave por prefix + hash do input); opcional (se cache_get/cache_set forem None, fallback não usa cache).
- **Conexões:** estendem `LLMConnection`; implementam `name`, `is_configured()`, `_ensure_llm()`, `invoke_vision`, `invoke_text`; "não configurado" retorna `_not_configured_response()` uniforme.

Ordem típica: **Gemini** (primário) → **OpenAI** → **Ollama**. O fallback não faz pré-cheque de `is_configured()`; cada conexão trata isso em invoke e retorna erro padronizado; o fallback segue para a próxima.

Se todas falharem: `{"error": "All LLM providers failed", "engine_errors": [...]}`. O módulo nunca lança; sempre retorna dict.

---

## 4. Agentes do pipeline

### 4.1 Diagram Agent

**Arquivo:** `app/threat_analysis/agents/diagram/agent.py`

- **Entrada:** imagem (bytes).
- **Saída:** JSON com `model`, `components` (id, type, name), `connections` (from, to, protocol), `boundaries` (trust boundaries).
- **Fluxo:** `run_vision_with_fallback()` com Gemini → OpenAI → Ollama, cache prefixo `"diagram"`, validação (dict com `components` lista).
- **Fallback em erro:** retorna objeto com um componente genérico (`"Unanalyzed Component"`) para o pipeline não quebrar.

### 4.2 STRIDE Agent

**Arquivo:** `app/threat_analysis/agents/stride/agent.py`

- **Entrada:** resultado do Diagram Agent (`components`, `connections`, `boundaries`).
- **Saída:** lista de ameaças com `component_id`, `threat_type`, `description`, `mitigation` (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege).
- **RAG:** base em `app/rag_data` (ChromaDB); RAGService com cache por processo; warm no startup da aplicação. Query fixa para contexto STRIDE; se RAG indisponível, segue sem contexto.
- **Fluxo:** `run_text_with_fallback()` com Gemini → OpenAI → Ollama, cache prefixo `"stride"`, validação (lista).
- **Fallback em erro:** retorna `[]`.

### 4.3 DREAD Agent

**Arquivo:** `app/threat_analysis/agents/dread/agent.py`

- **Entrada:** lista de ameaças do STRIDE.
- **Saída:** mesma lista com `dread_score` (média 1–10) e `dread_details` (Damage, Reproducibility, Exploitability, Affected users, Discoverability).
- **Fluxo:** se lista vazia retorna `[]`; senão `run_text_with_fallback()` com Gemini → OpenAI → Ollama, cache prefixo `"dread"`, validação (lista); pós-processamento limita dread_score em [1, 10].
- **Fallback em erro:** retorna a lista original sem scores.

---

## 5. Guardrail (validação de diagrama)

**Arquivo:** `app/threat_analysis/guardrails/architecture_diagram_validator.py`

Valida se a imagem é um **diagrama de arquitetura** antes de entrar no pipeline (Diagram → STRIDE → DREAD), evitando custo e respostas incoerentes.

- **Entrada:** `image_bytes`, `settings`.
- **Chamada:** `run_vision_with_fallback()` com Gemini → OpenAI → Ollama, **sem cache** (cada imagem reavaliada), validação com `is_architecture_diagram` e `reason`.
- **Aceito:** componentes de sistema, conexões/fluxos, trust boundaries (VPCs, subnets).
- **Rejeitado:** diagramas de sequência, fotos, fluxogramas, ilustrações genéricas, texto puro.
- **Em caso de erro do LLM:** o guardrail faz fail-open (não bloqueia; registra warning e permite a imagem).
- **Se não for diagrama:** levanta `ArchitectureDiagramValidationError`; o handler da API devolve **400** com a mensagem.

---

## 6. Specs e Postman

| Recurso                                            | Descrição                                                                                                      |
| -------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| **[specs/](specs/)**                               | Especificações (Spec Driven): contexto, requisitos, design, ADRs, modelo de dados, contratos de API, runbooks. |
| **[Postman Collections/](Postman%20Collections/)** | Coleções e ambiente para testes da API.                                                                        |

Para requisitos formais, decisões de arquitetura e contratos, use **specs/**; para testes manuais da API, use as coleções Postman.
