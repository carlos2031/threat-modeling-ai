# Roteiro de apresentação — CloudSec AI (até 10 min)

Roteiro passo a passo para apresentar o projeto em até 10 minutos: fluxo completo (upload → processamento → frontend), arquitetura e agentes de análise.

---

## Cronograma geral

| Bloco | Conteúdo | Tempo |
|-------|----------|-------|
| 1 | Abertura e problema | 0:00–1:00 |
| 2 | Arquitetura (containers e camadas) | 1:00–2:30 |
| 3 | Fluxo: upload e orquestrador | 2:30–4:00 |
| 4 | Pipeline de análise e agentes | 4:00–7:00 |
| 5 | Frontend e resultado final | 7:00–8:30 |
| 6 | Fechamento e próximos passos | 8:30–10:00 |

---

## 1. Abertura e problema (1 min)

**Fala:**  
"CloudSec AI é um sistema de análise de ameaças em diagramas de arquitetura. O problema: fazer threat modeling manual em diagramas é demorado e depende muito de quem analisa. A solução: enviar a imagem do diagrama e receber um relatório STRIDE com pontuação DREAD gerado por LLMs."

**Mostrar:**  
- Tela inicial do app (upload) ou slide com título + uma frase do problema.

**Tempo:** ~1 min.

---

## 2. Arquitetura — containers e camadas (1 min 30 s)

**Fala:**  
"A aplicação roda em containers. Frontend em React; orquestrador (threat-service) em FastAPI com Celery para tarefas assíncronas; threat-analyzer é o serviço que roda o pipeline LLM; PostgreSQL e Redis completam o stack."

**Mostrar:**  
- Diagrama de arquitetura do README (Mermaid: Browser → Frontend → threat-service → PG/Redis; Celery Worker → threat-analyzer).
- Ou slide com os 4 blocos: Usuário, Frontend, Orquestrador (API + Celery), Analyzer + Dados.

**Tempo:** ~1 min 30 s.

---

## 3. Fluxo: upload e orquestrador (1 min 30 s)

**Fala:**  
"O usuário envia o diagrama na tela inicial. O frontend chama POST /api/v1/analyses no threat-service. A API valida o arquivo, grava a imagem em disco, persiste um registro 'EM_ABERTO' no banco e devolve o ID da análise. O processamento não é na hora: o Celery Beat dispara a cada minuto uma varredura; o worker pega a primeira análise em aberto, marca como PROCESSANDO e chama o threat-analyzer."

**Mostrar:**  
- Fluxo na tela: fazer upload de um diagrama (ou mostrar screenshot).
- Opcional: trecho do código do controller (create_analysis) ou do Celery task (scan_pending_analyses → process_analysis).

**Tempo:** ~1 min 30 s.

---

## 4. Pipeline de análise e agentes (3 min)

**Fala (resumida):**  
"No threat-analyzer o fluxo é: guardrail → Diagram Agent → STRIDE Agent → DREAD Agent."

**4.1 Guardrail (~20 s)**  
"Primeiro o guardrail: um LLM de visão decide se a imagem é mesmo um diagrama de arquitetura. Se for foto ou fluxograma, devolve 400 e não gasta o resto do pipeline."

**Mostrar:**  
- Nome do arquivo ou trecho (architecture_diagram_validator).

**4.2 Diagram Agent (~45 s)**  
"O Diagram Agent recebe a imagem e usa um LLM com visão para extrair componentes, conexões e trust boundaries. A saída é um JSON com tipos e nomes de componentes e como eles se ligam. Esse JSON alimenta o próximo agente."

**Mostrar:**  
- Diagrama do pipeline (Guardrail → Diagram → STRIDE → DREAD) ou doc do docs/README.md.

**4.3 STRIDE Agent (~45 s)**  
"O STRIDE Agent recebe esse JSON e usa um LLM de texto para identificar ameaças por categoria STRIDE: Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege. Ele pode usar RAG com ChromaDB para enriquecer o contexto com uma base de conhecimento de ameaças."

**Mostrar:**  
- Lista STRIDE na doc ou no frontend (badges por tipo).

**4.4 DREAD Agent (~45 s)**  
"O DREAD Agent pega a lista de ameaças e atribui uma pontuação de 1 a 10 para cada uma (Damage, Reproducibility, Exploitability, Affected users, Discoverability). A média define o risco global: LOW, MEDIUM, HIGH ou CRITICAL."

**Mostrar:**  
- Exemplo de ameaça com dread_score e risk_level no relatório.

**Tempo total do bloco 4:** ~3 min.

---

## 5. Frontend e resultado final (1 min 30 s)

**Fala:**  
"Quando o worker termina, ele atualiza a análise no banco (status ANALISADO, resultado em JSON), cria uma notificação e o frontend pode exibir. Na lista de análises o usuário vê o status; ao abrir o detalhe, vê o diagrama, os componentes, as ameaças STRIDE com scores DREAD e o nível de risco. Também é possível descartar uma análise, com confirmação."

**Mostrar:**  
- Tela de listagem de análises e tela de detalhe de uma análise (relatório com ameaças e risco).
- Opcional: notificações e botão de descartar.

**Tempo:** ~1 min 30 s.

---

## 6. Fechamento (1 min 30 s)

**Fala:**  
"Resumindo: upload no frontend, orquestração e fila no threat-service, pipeline LLM no threat-analyzer com guardrail e três agentes (Diagram, STRIDE, DREAD), e resultado no frontend. Os LLMs usam fallback Gemini → OpenAI → Ollama e cache quando disponível. Testes unitários cobrem analyzer e service; para rodar tudo: make test na raiz."

**Mostrar:**  
- Slide de encerramento com stack (FastAPI, React, Celery, LLM, STRIDE/DREAD) ou README.

**Tempo:** ~1 min 30 s.

---

## Dicas de apresentação

- Manter demo ao vivo só se a stack estiver estável; senão usar screenshots ou vídeo curto.
- Se faltar tempo, encurtar o bloco 4 (agentes) para 2 min e alongar um pouco o bloco 5 (frontend).
- Ter um diagrama (AWS/Azure) em test-assets para upload na demo.
