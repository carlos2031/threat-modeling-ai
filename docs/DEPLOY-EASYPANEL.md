# Deploy do Threat Modeling AI no EasyPanel

Este guia descreve os passos para subir o projeto **Threat Modeling AI** no [EasyPanel](https://easypanel.io/).

## Visão geral da arquitetura

O projeto possui **8 serviços** que precisam ser orquestrados:

| Serviço | Descrição | Porta |
|---------|-----------|-------|
| postgres | Banco de dados PostgreSQL | 5432 |
| redis | Broker para Celery | 6379 |
| threat-analyzer | Pipeline LLM (STRIDE/DREAD) | 8000 |
| threat-service | API REST principal | 8000 |
| celery-worker | Processamento assíncrono | — |
| celery-beat | Agendador de tarefas | — |
| threat-frontend | UI React (nginx) | 80 |
| ollama | LLM local (opcional) | 11434 |

---

## Método recomendado: Docker Compose via Dockge

A forma mais simples de subir o stack completo no EasyPanel é usar o **Dockge**, um gerenciador de Docker Compose que pode ser instalado como template no EasyPanel.

### Passo 1: Instalar o EasyPanel

1. Acesse um dos provedores com instalação one-click:
   - [DigitalOcean](https://marketplace.digitalocean.com/apps/easypanel)
   - [AWS](https://aws.amazon.com/marketplace/pp/prodview-nkiq4lewjosjc)
   - [Vultr](https://www.vultr.com/marketplace/apps/easypanel)
   - [Linode](https://www.linode.com/marketplace/apps/easypanel/easypanel/)
   - [Hostinger](https://www.hostinger.com/)

2. Ou instale manualmente em um servidor Linux (Ubuntu recomendado, 2GB+ RAM):

```bash
curl -sSL https://get.docker.com | sh
docker run --rm -it \
  -v /etc/easypanel:/etc/easypanel \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  easypanel/easypanel setup
```

> **Importante:** As portas 80 e 443 devem estar livres.

### Passo 2: Instalar o Dockge no EasyPanel

1. No painel do EasyPanel, clique em **Templates**.
2. Procure por **Dockge** e instale (1-click).
3. Acesse o Dockge e faça login.

### Passo 3: Criar o stack no Dockge

1. No Dockge, clique em **Create Stack**.
2. Dê um nome ao stack (ex.: `threat-modeling-ai`).
3. Escolha **Deploy from Git** e informe:
   - **Repository URL:** URL do seu repositório (ex.: `https://github.com/seu-usuario/threat-modeling-ai.git`)
   - **Compose file path:** `docker-compose.easypanel.yml`
   - **Branch:** `main` (ou a branch desejada)

4. Ou use **Create from Compose** e cole o conteúdo do `docker-compose.easypanel.yml`.

### Passo 4: Configurar variáveis de ambiente

1. No Dockge, na stack criada, clique em **Edit** ou **Compose**.
2. Crie um arquivo `.env` na raiz do stack (ou use o editor de variáveis do Dockge) com o conteúdo baseado em `configs/.env.example`:

```env
# Obrigatórias
POSTGRES_USER=postgres
POSTGRES_PASSWORD=SENHA_SEGURA_AQUI
POSTGRES_DB=threat_modeling
DATABASE_URL=postgresql://postgres:SENHA_SEGURA_AQUI@postgres:5432/threat_modeling
REDIS_URL=redis://redis:6379/0

# LLM - use pelo menos um
GOOGLE_API_KEY=sua_chave_gemini
OPENAI_API_KEY=sua_chave_openai

# Ollama (se usar LLM local)
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=qwen2-vl

# CORS - ajuste com o domínio do seu frontend
CORS_ORIGINS=https://seu-dominio.com,http://localhost:80
```

3. **Importante:** Substitua `SENHA_SEGURA_AQUI` por uma senha forte e preencha as chaves de API (Gemini e/ou OpenAI).

### Passo 5: Deploy

1. Clique em **Deploy** no Dockge.
2. Aguarde o build das imagens (threat-analyzer, threat-service, threat-frontend) e o início dos containers.
3. Verifique os logs em caso de erro.

### Passo 6: Expor o frontend (domínio e proxy)

O EasyPanel usa Traefik como proxy reverso. Para expor o frontend:

1. No EasyPanel, localize o serviço **threat-frontend** (ou o container correspondente).
2. Adicione um **domínio** ao serviço (ex.: `threat-modeling.seudominio.com`).
3. Configure a **porta do proxy** como **80**.
4. O EasyPanel configurará HTTPS automaticamente via Let's Encrypt.

> **Nota:** Se estiver usando apenas o Dockge (fora do EasyPanel), você precisará configurar um proxy reverso (Nginx, Traefik ou Caddy) apontando para a porta 80 do container `threat-frontend`.

### Passo 7: (Opcional) Ollama e modelos de visão

Se quiser usar Ollama como fallback local:

1. O serviço `ollama` já está no compose.
2. Após o deploy, acesse o container Ollama e baixe o modelo:

```bash
docker exec -it <container_ollama> ollama pull qwen2-vl
```

---

## Método alternativo: App Services individuais no EasyPanel

Se preferir não usar Dockge, você pode criar cada serviço como **App Service** no EasyPanel. Este método é mais trabalhoso, pois exige configurar cada serviço separadamente.

### Pré-requisitos

- Criar um **Projeto** no EasyPanel (ex.: `threat-modeling`).
- Os serviços do mesmo projeto compartilham rede e se resolvem pelo nome.

### Ordem de criação

1. **PostgreSQL** – Use o template de banco ou crie um App com a imagem `postgres:15-alpine`.
2. **Redis** – App com imagem `redis:7-alpine`.
3. **threat-analyzer** – App com source = repositório Git, Dockerfile path = `threat-analyzer/Dockerfile`, Build context = raiz do repositório.
4. **threat-service** – App com source = repositório Git, Dockerfile path = `threat-service/Dockerfile`.
5. **celery-worker** – Mesma imagem do threat-service, com command: `celery -A app.celery_app worker -l info`.
6. **celery-beat** – Mesma imagem do threat-service, com command: `celery -A app.celery_app beat -l info`.
7. **threat-frontend** – App com source = repositório Git, Dockerfile path = `threat-frontend/Dockerfile`.

### Variáveis de ambiente

Para cada serviço, configure as variáveis conforme `configs/.env.example`. Os hostnames devem ser os **nomes dos serviços** no EasyPanel (ex.: `postgres`, `redis`, `threat-analyzer`).

### Ajuste do frontend

O `threat-frontend` usa nginx e faz proxy de `/api/v1/` para `http://threat-service:8000`. No EasyPanel, o nome do serviço pode ser diferente (ex.: `threat-modeling-threat-service`). Nesse caso, será necessário ajustar o `threat-frontend/nginx/default.conf` ou criar um proxy reverso no EasyPanel que encaminhe `/api/v1/` para o threat-service.

---

## Checklist pós-deploy

- [ ] Frontend acessível no domínio configurado
- [ ] API respondendo em `/api/v1/health`
- [ ] Upload de diagrama funcionando
- [ ] Análise sendo processada (verificar logs do celery-worker)
- [ ] Chaves de LLM (Gemini/OpenAI) configuradas ou Ollama com modelo baixado

---

## Troubleshooting

### Erro de conexão com o banco

- Verifique se `DATABASE_URL` usa o hostname correto do serviço PostgreSQL.
- No EasyPanel/Dockge, o hostname costuma ser o nome do serviço (ex.: `postgres`).

### Frontend não carrega a API

- O nginx do frontend espera `threat-service` na rede. Confirme que ambos estão na mesma rede Docker.
- Se usar proxy do EasyPanel, pode ser necessário expor o threat-service e configurar CORS.

### Celery não processa tarefas

- Verifique `REDIS_URL` e `ANALYZER_URL`.
- Confira os logs do `celery-worker` e do `threat-analyzer`.

### Build falha no threat-analyzer/threat-service

- Os Dockerfiles usam `context: .` (raiz do repositório). O build deve ser executado a partir da raiz do projeto.
- No EasyPanel App Service, defina o **Build context** como a raiz do repositório e o **Dockerfile path** como `threat-analyzer/Dockerfile` (ou o correspondente).
