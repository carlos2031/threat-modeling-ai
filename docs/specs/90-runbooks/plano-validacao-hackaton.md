# Plano de Validação — Hackaton FIAP (Threat Modeling AI)

**Objetivo:** Validar o projeto threat-modeling-ai com testes de funcionamento, documentação, revisão de código e roteiro de apresentação. Inclui uso do projeto contraparte (fiap-hackaton-fase05) como protótipo 1 (YOLO) e threat-modeling-ai como protótipo 2 (LLM).

**Contexto:** Documentação oficial em `docs/` (Spec-Driven). A pasta `notebooks/` foi copiada para o contexto privado (`private-context/notebooks/`) e removida do repositório.

**Data:** 2026-02-23

---

## 1. Testes de validação e funcionamento

### 1.1 Testes unitários (por serviço)

| Serviço                       | Comando                        | Pré-requisito                                                                    |
| ----------------------------- | ------------------------------ | -------------------------------------------------------------------------------- |
| threat-analyzer               | `make -C threat-analyzer test` | `.venv` na raiz; PYTHONPATH=threat-analyzer:threat-modeling-shared               |
| threat-service (orquestrador) | `make -C threat-service test`  | `.venv` na raiz; PostgreSQL com DB `threat_modeling_test` ou `TEST_DATABASE_URL` |

**Nota:** O diretório do orquestrador é **threat-service**. README e `pre_commit.sh` foram atualizados para `make -C threat-service` e `make -C threat-frontend`.

**Checklist:**

- [ ] `make setup-backend` (ou `make setup`) executado na raiz.
- [ ] `createdb threat_modeling_test` (ou equivalente) para testes do orquestrador.
- [ ] `make -C threat-analyzer test` — todos passando.
- [ ] `make -C threat-service test` — todos passando (e lint se desejado).

### 1.2 Testes em container (CI)

- [ ] `make -C threat-analyzer test-image` (build stage test + pytest no container).
- [ ] `make -C threat-service test-image` (idem para orquestrador).

### 1.3 Fluxo de análise (e2e manual)

- [ ] `make run` (ou `make run-detached`) sobe a stack completa.
- [ ] Frontend acessível (porta 80 ou a configurada).
- [ ] Upload de diagrama via UI → 201 → status passa a PROCESSANDO → ANALISADO.
- [ ] Detalhe da análise exibe relatório STRIDE/DREAD.
- [ ] `make test-analysis-flow`: script envia imagens de teste ao threat-analyzer e exibe resposta (requer stack rodando).

### 1.4 Projeto contraparte (fiap-hackaton-fase05-ref)

- [ ] Clonado em `Projetos/Ativos/fiap-hackaton-fase05-ref`.
- [ ] `pip install -e ".[dev]"` (ou `make dev`); modelo `best.pt` em `models/` se disponível.
- [ ] `make db-up` (PostgreSQL); `make run` (Streamlit).
- [ ] Upload de diagrama de teste → detecção YOLO + análise STRIDE exibidas.

---

## 2. Documentação

### 2.1 Spec-Driven (`docs/specs/`)

- [ ] **00-context:** problem-statement, system-context, glossary, stack-e-libs, guidelines atualizados.
- [ ] **10-requirements:** PRD e requisitos funcionais alinhados ao fluxo atual (LLM, sem YOLO em produção).
- [ ] **20-design:** architecture, data-model, api-contracts, sequence/flow de análise assíncrona.
- [ ] **90-decisions:** ADRs (ex.: ADR-0001 pipeline LLM, ADR-0002 API-first, etc.) consistentes.
- [ ] **99-meta:** justificativa-uso-llm, test-conventions, assumptions, open-questions; llm-selecao-validacao e model-evaluation-report se aplicável.

### 2.2 Runbooks e roteiros (`docs/specs/90-runbooks/`)

- [ ] **plano-validacao-hackaton.md** (este arquivo) — executado e checklist atualizado.
- [ ] **Análise da contraparte YOLO** — em contexto privado (`private-context/analise-contraparte-yolo.md`), não versionada.
- [ ] **roteiro-apresentacao-prototipo1-prototipo2.md** — roteiro mestre (YOLO → LLM).

### 2.3 Documentação explicativa (`docs/README.md`)

- [ ] **docs/README.md** — Explicação unificada (fluxo, ThreatModelService, LLM, agentes, guardrail) revisada e alinhada ao comportamento atual. A pasta `docs/explicativo/` contém apenas um README que redireciona para `docs/README.md`.

### 2.4 README e Postman

- [ ] README raiz: comandos de teste corretos (`threat-service` em vez de `threat-modeling-api` se for o caso).
- [ ] Postman: coleção e ambiente em `docs/Postman Collections/` testados contra API local.

### 2.5 Notebooks → docs

- [x] Pasta `notebooks/` copiada para `private-context/notebooks/` e removida do repositório.
- [x] Referências na documentação apontam apenas para `docs/` (specs + docs/README.md).

---

## 3. Revisão de código

- [ ] **threat-analyzer:** lint (`make -C threat-analyzer lint`), estrutura de testes espelhando `app/` (conforme `docs/specs/99-meta/test-conventions.md`).
- [ ] **threat-service:** lint, testes e convenção de testes; consistência de nomenclatura (threat-modeling-api vs threat-service na doc e no código).
- [ ] **threat-modeling-shared:** lint (ruff) executado (ex.: via `pre_commit.sh`).
- [ ] **threat-frontend:** lint (ex.: `make -C threat-frontend lint` ou npm/ESLint).
- [ ] Sem credenciais ou segredos em código; uso de `configs/.env` e variáveis de ambiente.
- [ ] Pre-commit: `pre-commit run --all-files` (ou `./scripts/pre_commit.sh`) — ajustar referências de `threat-modeling-api` para `threat-service` onde for o diretório real.

---

## 4. Roteiro de apresentação

- [ ] Roteiro mestre lido e ensaiado: **docs/specs/90-runbooks/roteiro-apresentacao-prototipo1-prototipo2.md**.
- [ ] Protótipo 1 (YOLO): repositório fiap-hackaton-fase05 ou cópia local; roteiro original em `docs/roteiro_video.md` do repo de referência.
- [ ] Protótipo 2 (LLM): threat-modeling-ai; demonstração com `make run`, upload, listagem, detalhe e (opcional) Postman.
- [ ] Comparativo final (YOLO vs LLM) e encerramento conforme roteiro.

---

## 5. Ordem sugerida de execução

1. **Setup e testes automatizados** — setup backend, criar DB de teste, rodar testes do analyzer e do service (e test-image se for CI).
2. **Ajustes de documentação** — README, pre_commit e specs (nomenclatura threat-service vs threat-modeling-api).
3. **Runbooks e roteiro** — validar análise da contraparte e roteiro mestre; ensaio da apresentação.
4. **Fluxo e2e e revisão** — `make run`, test-analysis-flow, revisão de lint e convenções.
5. **Notebooks** — concluído: copiados para `private-context/notebooks/` e removidos do repositório.

---

## 6. Referências

- [test-conventions.md](../99-meta/test-conventions.md)
- [architecture.md](../20-design/architecture.md)
- Análise da contraparte YOLO: `private-context/analise-contraparte-yolo.md` (contexto privado).
- [roteiro-apresentacao-prototipo1-prototipo2.md](./roteiro-apresentacao-prototipo1-prototipo2.md)
- Contexto dos agentes: projeto cursor-multiagent-system (Infraestrutura), `config/CONTEXTO_GERAL.md`
