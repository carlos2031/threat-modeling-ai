# Roteiro de Apresentação — Protótipo 1 (YOLO) e Protótipo 2 (LLM)

**Objetivo:** Mestrar a apresentação do Hackaton FIAP posicionando dois abordagens: primeiro o **Cloud Architecture Security Analyzer** (YOLO) como protótipo inicial; em seguida o **Threat Modeling AI** (LLM) como segunda alternativa.

**Formato sugerido:** Gravação de tela + narração (ou apresentação ao vivo). Cada seção indica **o que mostrar** e **o que falar**.

---

## Parte A — Protótipo 1: Cloud Architecture Security Analyzer (YOLO)

**Referência:** [fiap-hackaton-fase05](https://github.com/renato-penna/fiap-hackaton-fase05) e [roteiro_video.md](https://github.com/renato-penna/fiap-hackaton-fase05/blob/main/docs/roteiro_video.md).

### Cena 1 — Abertura do Protótipo 1 (≈ 30 s)

**Tela:** README ou tela inicial do projeto YOLO (repositório ou VS Code).

**Fala:**

> Este é o primeiro protótipo: o **Cloud Architecture Security Analyzer**. A ideia é direta: você faz upload de um diagrama de arquitetura cloud — AWS, Azure ou GCP — e a aplicação **detecta os componentes** usando um modelo **YOLO** treinado (visão computacional) e aplica a metodologia **STRIDE** com uma base de conhecimento fixa no código. Tudo roda **100% local**, sem API externa e sem custo por requisição.

---

### Cena 2 — Problema e motivação (≈ 45 s)

**Tela:** Diagrama de exemplo (ex.: arquitetura AWS).

**Fala:**

> A análise de segurança em diagramas costuma ser manual: um especialista revisa componente a componente. Há soluções que usam LLMs (GPT, Claude) para analisar diagramas, mas isso gera **custo contínuo** por token. Neste primeiro protótipo, eliminamos esse custo: **YOLO** para detecção e uma **base STRIDE local** para as ameaças. Custo operacional praticamente zero após o deploy.

---

### Cena 3 — Dataset, preparação e treino (≈ 1 min 30 s)

**Tela:** No projeto de referência (fiap-hackaton-fase05): scripts `script/prepare_dataset.py`, `script/analyze_dataset.py`, notebook `notebooks/train_colab.ipynb`.

**Fala:**

> O dataset vem do Kaggle (diagramas anotados). O script de preparação converte anotações (ex.: LabelMe) para Pascal VOC, mescla anotações customizadas e gera um pacote pronto para o Colab. O treino foi feito no **Google Colab** com **checkpoints no Drive**: a cada 5 épocas o modelo é salvo e o treino pode ser retomado com `resume=True`. Usamos **YOLOv8n** (nano) para caber no free tier. Mais de 60 classes do Kaggle foram mapeadas para **15 categorias** alinhadas ao STRIDE (compute, database, storage, network, security, etc.).

---

### Cena 4 — Arquitetura e demonstração (≈ 1 min)

**Tela:** Estrutura do projeto (config, src/detection, src/stride, src/database, src/app.py), depois `make db-up` e `make run`.

**Fala:**

> O projeto é modular: configuração com dataclasses frozen e dotenv, detecção com YOLO em lazy loading, módulo STRIDE com categorias, base de ameaças e engine que monta o relatório. A interface é **Streamlit**: upload, slider de confiança, imagem com bounding boxes e análise STRIDE por componente. O histórico fica no PostgreSQL. Temos **71 testes** (detector, knowledge_base, stride_engine), Ruff e MyPy em modo strict.

**Tela:** Upload de um diagrama e resultado com bounding boxes + análise STRIDE.

---

### Cena 5 — Vantagens do Protótipo 1 (≈ 30 s)

**Fala:**

> Resumindo o primeiro protótipo: **custo zero** após o deploy, **privacidade total** (nada sai da máquina), **multi-cloud** (AWS, Azure, GCP), código **testado e tipado**. A limitação é a dependência do **treino YOLO**: qualidade e tempo de treino; para novos componentes é preciso retreinar.

---

## Parte B — Protótipo 2: Threat Modeling AI (LLM)

**Referência:** Este repositório (threat-modeling-ai), documentação em `docs/specs/` e `docs/README.md` (explicação unificada).

### Cena 6 — Transição para o Protótipo 2 (≈ 30 s)

**Tela:** README ou arquitetura do threat-modeling-ai (`docs/specs/20-design/architecture.md`).

**Fala:**

> O **segundo protótipo** — Threat Modeling AI — troca a detecção por **LLMs com visão**. Em vez de um modelo YOLO treinado, usamos um **pipeline LLM**: primeiro um agente de diagrama extrai componentes e conexões da imagem; em seguida o **StrideAgent** com **RAG** identifica ameaças STRIDE; e o **DreadAgent** aplica a pontuação **DREAD**. Há fallback entre provedores: Gemini, OpenAI e Ollama (local). Toda a documentação e decisões estão em **spec-driven** em `docs/specs/`.

---

### Cena 7 — Arquitetura e fluxo (≈ 1 min)

**Tela:** Diagrama de arquitetura (orquestrador, threat-analyzer, Celery, PostgreSQL, Redis, frontend).

**Fala:**

> O sistema tem **dois backends**: o **orquestrador** (API principal) recebe o upload, persiste a análise e dispara o processamento em background via **Celery**. O **threat-analyzer** recebe a imagem por HTTP e executa o pipeline: guardrail (é diagrama?), DiagramAgent, StrideAgent com RAG, DreadAgent. O frontend em **React** consome só a API do orquestrador: upload, listagem, detalhe com polling e notificações. Processamento **assíncrono** evita timeout e permite escalar.

---

### Cena 8 — Decisão LLM vs YOLO e documentação (≈ 45 s)

**Tela:** `docs/specs/99-meta/justificativa-uso-llm.md` e ADR-0001.

**Fala:**

> A decisão de usar **LLM como principal** está registrada em ADR e na justificativa: o treino YOLO nos nossos datasets ficou aquém do desejado no prazo do Hackaton; o pipeline LLM já entregava análise estável. O trabalho de YOLO nos notebooks foi **preservado** para uma fase futura (híbrido YOLO + fallback LLM). Toda a especificação — contexto, requisitos, design, ADRs — fica em `docs/specs/`, seguindo **Spec-Driven Development**; a pasta **notebooks** foi movida para o contexto privado (`private-context/notebooks/`) e removida do repositório; a documentação oficial está em `docs/`.

---

### Cena 9 — Demonstração do Protótipo 2 (≈ 1 min 30 s)

**Tela:** `make run` (ou stack já rodando), frontend, upload de diagrama, listagem, detalhe da análise.

**Fala:**

> Subindo a stack com `make run`: frontend, orquestrador, threat-analyzer, PostgreSQL, Redis e Celery. Faço upload de um diagrama; a API devolve 201 e o processamento segue em background. Na listagem acompanho o status; ao concluir, abro o detalhe e vejo o relatório STRIDE/DREAD, componentes, conexões e ameaças com mitigação. Posso usar Postman para testar a API; as coleções estão em `docs/Postman Collections/`.

---

### Cena 10 — Comparativo e encerramento (≈ 1 min)

**Tela:** Tabela comparativa ou slide (YOLO vs LLM).

**Fala:**

> **Protótipo 1 (YOLO):** custo zero, privacidade total, 100% local; exige treino e manutenção do modelo. **Protótipo 2 (LLM):** flexível, sem treino de visão, DREAD e RAG; custo por token (ou Ollama local) e dependência de provedor. Os dois atendem ao objetivo de **identificar componentes e gerar análise STRIDE**; a escolha depende de orçamento, privacidade e integração com o resto do sistema. Obrigado.

---

## Resumo de tempos (sugestão)

| Parte     | Conteúdo                   | Duração           |
| --------- | -------------------------- | ----------------- |
| A.1       | Abertura Protótipo 1       | 30 s              |
| A.2       | Problema e motivação       | 45 s              |
| A.3       | Dataset e treino YOLO      | 1 min 30 s        |
| A.4       | Arquitetura e demo YOLO    | 1 min             |
| A.5       | Vantagens Protótipo 1      | 30 s              |
| B.6       | Transição Protótipo 2      | 30 s              |
| B.7       | Arquitetura LLM            | 1 min             |
| B.8       | Decisão LLM e docs         | 45 s              |
| B.9       | Demo Protótipo 2           | 1 min 30 s        |
| B.10      | Comparativo e encerramento | 1 min             |
| **Total** |                            | **≈ 10 min 30 s** |

---

## Referências

- Análise da contraparte YOLO: contexto privado (`private-context/analise-contraparte-yolo.md`), não versionada.
- [Roteiro vídeo original (YOLO)](https://github.com/renato-penna/fiap-hackaton-fase05/blob/main/docs/roteiro_video.md)
- [Arquitetura threat-modeling-ai](../20-design/architecture.md)
- [Justificativa uso LLM](../99-meta/justificativa-uso-llm.md)
- [ADR-0001 — Pipeline LLM](../90-decisions/ADR-0001-pipeline-llm-principal.md)
