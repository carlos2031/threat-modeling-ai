# Fluxo Basico de Analise

Este documento descreve o fluxo completo para construir a base RAG, subir a API do threat-analyzer e executar analises de diagramas de arquitetura (com exemplos de requisicao e resposta).

## Objetivo

1. **Construir a base RAG** a partir dos arquivos em `notebooks/knowledge-base/input_files` (STRIDE/DREAD). O resultado e gravado em `threat-analyzer/app/rag_data` e usado pelo agente STRIDE para enriquecer o contexto do LLM.
2. **Subir o threat-analyzer** (ou a stack completa via Docker).
3. **Enviar imagens de diagramas** para o endpoint `POST /api/v1/threat-model/analyze` e obter a resposta com componentes, conexoes, ameacas STRIDE e pontuacao DREAD.

## Pre-requisitos

- Python 3.10+ e dependencias do projeto (por exemplo `make setup-backend` na raiz).
- Para processar a base RAG: Docling instalado no ambiente dos notebooks (`make setup-notebooks` ou dependencias do script de RAG).
- API rodando: threat-analyzer em `http://localhost:8001` (quando sobe via Docker a partir da raiz).

---

## 1. Construcao da base RAG

A base de conhecimento (arquivos .md, e conversao de PDF/DOCX via Docling) e processada e copiada para `threat-analyzer/app/rag_data`. O STRIDE Agent usa essa pasta para RAG; sem ela, a analise segue apenas com o contexto do LLM.

**Comando (na raiz do projeto):**

```bash
make process-rag-kb
```

Isso executa `notebooks/scripts/rag_processing/process_knowledge_base.py`, que:

- Converte/copia arquivos em `notebooks/knowledge-base/input_files/stride` e `.../dread` para `notebooks/knowledge-base/output_files/stride` e `.../dread`.
- Gera o arquivo unico comprimido `notebooks/knowledge-base/rag_knowledge_base.tar.gz`.
- Copia o conteudo de `output_files` para `threat-analyzer/app/rag_data/` (stride e dread).

Apos esse passo, ao iniciar o threat-analyzer, o retriever RAG e construido no startup (warm cache) e reutilizado nas requisicoes.

---

## 2. Subir a aplicacao

Na raiz do projeto:

```bash
make run
```

Isso sobe todos os servicos via Docker Compose, incluindo o **threat-analyzer** na porta **8001**. O health check e feito em `http://localhost:8001/health/`.

Para testar apenas o threat-analyzer (sem frontend/service/celery), pode-se subir so os servicos necessarios ou o container do threat-analyzer.

---

## 3. Testar o fluxo de analise

### 3.1 Script Python (recomendado)

O script `scripts/run_analysis_flow.py` (na raiz do projeto) envia uma ou mais imagens para o endpoint de analise e imprime um resumo da resposta (model_used, componentes, conexoes, ameacas, risk_level, processing_time).

**Uso basico (na raiz do projeto):**

```bash
# Garantir que a API esta rodando (make run em outro terminal).
# Opcional: construir RAG antes.
make process-rag-kb

# Executar o fluxo com as imagens padrao (notebooks/assets/diagram01.png e diagram02.png)
PYTHONPATH=. python scripts/run_analysis_flow.py
```

**Construir RAG e em seguida testar (sem subir a API pelo script):**

```bash
PYTHONPATH=. python scripts/run_analysis_flow.py --build-rag
# A API ainda precisa estar rodando (make run).
PYTHONPATH=. python scripts/run_analysis_flow.py
```

**Outras opcoes:**

```bash
# URL do analyzer (default: http://localhost:8001)
PYTHONPATH=. python scripts/run_analysis_flow.py --base-url http://localhost:8001

# Imagens especificas (pode repetir --image)
PYTHONPATH=. python scripts/run_analysis_flow.py --image notebooks/assets/diagram01.png --image path/to/outro.png

# Salvar a ultima resposta JSON em arquivo
PYTHONPATH=. python scripts/run_analysis_flow.py --save output/analise.json
```

O script usa a biblioteca `httpx` (ja dependencia do threat-analyzer). A saida esperada inclui linhas como:

- `Status: OK`
- `model_used`, `components`, `connections`, `threats`, `risk_level`, `risk_score`, `processing_time`

---

### 3.2 Requisicao com curl

O endpoint e **POST** em **multipart/form-data**. O campo obrigatorio e **file** (imagem do diagrama). Opcionalmente pode-se enviar **confidence** e **iou** como campos de formulario (reservados para uso futuro).

**Exemplo de requisicao (sucesso):**

```bash
curl -X POST http://localhost:8001/api/v1/threat-model/analyze \
  -F "file=@notebooks/assets/diagram01.png"
```

**Exemplo com parametros opcionais (confidence e iou):**

```bash
curl -X POST http://localhost:8001/api/v1/threat-model/analyze \
  -F "file=@notebooks/assets/diagram01.png" \
  -F "confidence=0.5" \
  -F "iou=0.5"
```

**Tipos de imagem aceitos:** `image/png`, `image/jpeg`, `image/webp`, `image/gif`. O content-type e inferido pelo nome do arquivo no curl.

**Exemplo de resposta (200 OK):**

O corpo e JSON no formato do schema `AnalysisResponse`:

- **model_used**: identificador do modelo LLM usado (ex.: gemini-1.5-pro).
- **components**: lista de componentes extraidos do diagrama (id, type, name, description).
- **connections**: lista de conexoes (from_id, to_id, protocol, description, encrypted).
- **threats**: lista de ameacas STRIDE com mitigacao e detalhes DREAD (dread_score, dread_details).
- **risk_score**: numero de 0 a 10 (media dos escores DREAD).
- **risk_level**: LOW | MEDIUM | HIGH | CRITICAL.
- **processing_time**: tempo total em segundos.

Exemplo reduzido:

```json
{
  "model_used": "gemini-1.5-pro",
  "components": [
    {
      "id": "1",
      "type": "Server",
      "name": "API Backend",
      "description": "Main application server"
    }
  ],
  "connections": [
    {
      "from_id": "1",
      "to_id": "2",
      "protocol": "HTTPS",
      "description": null,
      "encrypted": true
    }
  ],
  "threats": [
    {
      "component_id": "1",
      "threat_type": "Spoofing",
      "description": "...",
      "mitigation": "...",
      "dread_score": 4.2,
      "dread_details": { "D": 4, "R": 4, "E": 5, "A": 4, "D": 4 }
    }
  ],
  "risk_score": 4.1,
  "risk_level": "MEDIUM",
  "processing_time": 12.34
}
```

**Casos de erro comuns:**

- **400 Bad Request – tipo de arquivo invalido:** enviar um arquivo que nao e imagem (ex.: PDF). Resposta contem `detail` com mensagem do tipo "Invalid file type".
- **400 Bad Request – diagrama rejeitado pelo guardrail:** a imagem nao foi considerada um diagrama de arquitetura valido. Resposta contem `detail` com o motivo.
- **500 Internal Server Error:** falha interna (ex.: LLM indisponivel, erro de configuracao). Resposta pode incluir `detail` e `details`.

Exemplo de resposta de erro (400):

```json
{
  "detail": "Invalid file type: application/pdf. Allowed: image/png, image/jpeg, image/webp, image/gif."
}
```

---

## 4. Ordem recomendada para validar a API

1. **Construir RAG:** `make process-rag-kb`
2. **Subir a stack:** `make run` (ou apenas os servicos do threat-analyzer/redis se aplicavel).
3. **Aguardar o health:** `curl -s http://localhost:8001/health/` deve retornar 200.
4. **Rodar o script de fluxo:** `PYTHONPATH=. python scripts/run_analysis_flow.py`
5. **Opcional:** repetir com `curl` usando as imagens em `notebooks/assets/` e inspecionar o JSON completo.

Com isso, o fluxo basico de analise (RAG + envio de imagem + resposta STRIDE/DREAD) fica coberto e documentado.
