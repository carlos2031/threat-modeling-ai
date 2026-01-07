# ArchThreat Analyzer

**Sistema de Modelagem de Ameaças com IA baseado em STRIDE**

Projeto desenvolvido para o Hackathon FIAP - Fase 5 (Tech Challenger).

## 📋 Sobre o Projeto

O **ArchThreat Analyzer** é um sistema de Inteligência Artificial que realiza automaticamente a modelagem de ameaças baseada na metodologia STRIDE, a partir de diagramas de arquitetura de software em imagem.

### Funcionalidades Principais

- 📤 Upload e processamento de imagens de diagramas de arquitetura
- 🔍 Identificação automática de componentes arquiteturais
- 🛡️ Análise STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege)
- 📊 Geração de relatórios estruturados de ameaças
- 📥 Exportação de relatórios em múltiplos formatos (PDF, JSON, CSV)
- 📚 Histórico de análises realizadas

## 🏗 Arquitetura

```
┌─────────────────┐
│   Frontend      │
│   (React)       │
└────────┬────────┘
         │
┌────────▼────────┐
│   Backend API   │
│   (FastAPI)     │
└────────┬────────┘
    ┌────┴────┐
    │        │
┌───▼───┐ ┌──▼────┐
│  LLM  │ │  DB   │
│  API  │ │(Postgres)│
└───────┘ └────────┘
```

## 🛠 Stack Tecnológica

### Backend
- **FastAPI** (Python 3.11+)
- **PostgreSQL 15+**
- **OpenAI GPT-4 Vision** / **Claude 3.5 Sonnet**
- **Pillow** (processamento de imagens)
- **Pydantic v2** (validação)
- **pytest** (testes)

### Frontend
- **React 18** com **TypeScript**
- **Vite** (build tool)
- **TailwindCSS** (estilização)
- **React Query** (gerenciamento de estado)
- **Axios** (requisições HTTP)

### Infraestrutura
- **Docker** e **Docker Compose**
- **Nginx** (servidor web)

## 📁 Estrutura do Projeto

```
threat-modeling-ai/
├── arch-threat-backend/     # API FastAPI
├── arch-threat-frontend/    # Aplicação React
├── notebooks/               # Jupyter notebooks para análise
├── docs/                    # Documentação técnica
├── scripts/                 # Scripts utilitários
└── Documentacao/            # Documentação do projeto (não versionado)
```

## 🚀 Início Rápido

### Pré-requisitos

- Docker e Docker Compose
- Python 3.11+ (para desenvolvimento local)
- Node.js 20+ (para desenvolvimento frontend)

### Instalação

```bash
# Clone o repositório
git clone <repository-url>
cd threat-modeling-ai

# Configure as variáveis de ambiente
cp .env.example .env
# Edite .env com suas configurações

# Inicie os serviços
docker compose up -d
```

### Desenvolvimento

```bash
# Backend
cd arch-threat-backend
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows
pip install -r requirements-dev.txt
uvicorn app.main:app --reload

# Frontend
cd arch-threat-frontend
npm install
npm run dev
```

## 📚 Documentação

- [Documentação Técnica](Documentacao/DOCUMENTACAO_TECNICA.md)
- [Planejamento de Etapas](Documentacao/PLANEJAMENTO_ETAPAS.md)
- [API Documentation](docs/API.md) (em construção)

## 🧪 Testes

```bash
# Backend
cd arch-threat-backend
pytest

# Com cobertura
pytest --cov=app --cov-report=html
```

## 📅 Cronograma

- **Início:** 13/01/2026
- **Entrega:** 20/02/2026
- **Duração:** 5 semanas + 1 semana de buffer

## 📝 Licença

Este projeto foi desenvolvido para o Hackathon FIAP - Fase 5.

## 👤 Autor

Lucas Biason

---

**Status do Projeto:** 🚧 Em Desenvolvimento

