#!/usr/bin/env python3
"""
Script para criar cards no Notion para o projeto ArchThreat Analyzer.

Este script cria:
1. Card principal do projeto
2. Subitens para cada fase/etapa do planejamento

Uso:
    python scripts/create_notion_cards.py
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Adicionar ao path para importar o módulo do Notion
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "Infraestrutura" / "my-local-place" / "services" / "external" / "notion-automation-suite" / "src"))

try:
    from custom.study_notion import StudyNotion
    from core.notion_service import NotionService
    from utils.constants import StudiesStatus, Priority
except ImportError as e:
    print(f"❌ Erro ao importar módulos do Notion: {e}")
    print("Certifique-se de que o caminho do módulo está correto.")
    sys.exit(1)

# Database ID da base Studies
STUDIES_DATABASE_ID = "1fa962a7-693c-80de-b90b-eaa513dcf9d1"

# Timezone de São Paulo
SAO_PAULO_TZ = timezone(timedelta(hours=-3))


async def create_project_cards():
    """Cria os cards do projeto no Notion."""
    
    # Obter token do Notion (deve estar configurado no ambiente)
    import os
    token = os.getenv("NOTION_API_TOKEN")
    
    if not token:
        print("❌ Erro: NOTION_API_TOKEN não encontrado nas variáveis de ambiente.")
        print("Configure a variável de ambiente NOTION_API_TOKEN antes de executar este script.")
        sys.exit(1)
    
    # Inicializar serviços
    service = NotionService(token=token)
    study = StudyNotion(service, STUDIES_DATABASE_ID)
    
    print("🚀 Criando cards no Notion para ArchThreat Analyzer...\n")
    
    # Card principal do projeto
    print("📌 Criando card principal do projeto...")
    project_card = await study.create_card(
        title="ArchThreat Analyzer - Hackathon FIAP Fase 5",
        status=StudiesStatus.PARA_FAZER.value,
        categorias=["FIAP", "IA", "Inteligência Artificial", "Segurança", "Arquitetura de Software", "Projeto", "Portfolio"],
        prioridade=Priority.ALTA.value,
        periodo={
            "start": "2026-01-13",
            "end": "2026-02-20"
        },
        tempo_total="150:00:00",  # ~150 horas estimadas
        descricao="""Sistema de Modelagem de Ameaças com IA baseado em STRIDE.

**Objetivo:**
Desenvolver um sistema de Inteligência Artificial que realiza automaticamente a modelagem de ameaças baseada na metodologia STRIDE, a partir de diagramas de arquitetura de software em imagem.

**Funcionalidades Principais:**
- Upload e processamento de imagens de diagramas de arquitetura
- Identificação automática de componentes arquiteturais
- Análise STRIDE completa
- Geração de relatórios estruturados
- Exportação em múltiplos formatos (PDF, JSON, CSV)

**Stack:**
- Backend: FastAPI (Python 3.11+)
- Frontend: React 18 + TypeScript
- IA: OpenAI GPT-4 Vision / Claude 3.5 Sonnet
- Database: PostgreSQL 15+

**Repositório:** `/home/lucas-biason/Projetos/Projetos/threat-modeling-ai`
**Documentação:** Ver pasta `Documentacao/`
""",
        icon="🛡️"
    )
    
    project_id = project_card['id']
    project_url = f"https://www.notion.so/{project_id.replace('-', '')}"
    print(f"✅ Card principal criado: {project_url}\n")
    
    # Fases do projeto (baseadas no PLANEJAMENTO_ETAPAS.md)
    phases = [
        {
            "title": "Semana 1: Aprendizado e Planejamento",
            "periodo": {"start": "2026-01-13", "end": "2026-01-19"},
            "descricao": """Aprendizado teórico sobre STRIDE e Diagramas de Arquitetura.

**Tarefas:**
- Estudar STRIDE via NotebookLM
- Estudar Diagramas de Arquitetura via NotebookLM
- Revisar documentação técnica
- Definir arquitetura detalhada
- Configurar ambiente de desenvolvimento

**Entregáveis:**
- Resumo de conceitos STRIDE
- Guia de identificação de componentes
- Arquitetura detalhada definida
- Prompts para LLM
""",
            "tempo_total": "25:00:00"
        },
        {
            "title": "Semana 2: Setup e Infraestrutura",
            "periodo": {"start": "2026-01-20", "end": "2026-01-26"},
            "descricao": """Configuração do ambiente de desenvolvimento e infraestrutura base.

**Tarefas:**
- Criar repositório Git
- Configurar Docker e Docker Compose
- Configurar banco de dados PostgreSQL
- Estrutura inicial de código (Backend e Frontend)
- Setup de testes e CI/CD básico

**Entregáveis:**
- Repositório configurado
- Docker funcionando
- Banco de dados configurado
- Estrutura base criada
""",
            "tempo_total": "30:00:00"
        },
        {
            "title": "Semana 3: Backend - Core",
            "periodo": {"start": "2026-01-27", "end": "2026-02-02"},
            "descricao": """Implementação dos serviços core do sistema.

**Tarefas:**
- Image Service (processamento de imagens)
- LLM Service (integração com OpenAI/Claude)
- STRIDE Service (lógica de análise)
- Report Service (geração de relatórios)
- Testes unitários

**Entregáveis:**
- Todos os serviços implementados
- Testes unitários > 80% cobertura
""",
            "tempo_total": "35:00:00"
        },
        {
            "title": "Semana 4: Backend - API",
            "periodo": {"start": "2026-02-03", "end": "2026-02-09"},
            "descricao": """Implementação dos endpoints da API e integração completa.

**Tarefas:**
- Routers e Controllers
- Schemas e Validação (Pydantic)
- Integração com Banco de Dados
- Testes de integração
- Documentação Swagger/OpenAPI

**Entregáveis:**
- API completa e funcional
- Documentação Swagger completa
- Postman collection
""",
            "tempo_total": "35:00:00"
        },
        {
            "title": "Semana 5: Frontend e Integração",
            "periodo": {"start": "2026-02-10", "end": "2026-02-16"},
            "descricao": """Implementação da interface web e integração com backend.

**Tarefas:**
- Componentes base (ImageUpload, AnalysisProgress)
- Componentes de visualização (ComponentList, ThreatMatrix)
- Relatórios (ReportViewer, ReportExport)
- Integração com API
- UX e polimento

**Entregáveis:**
- Frontend completo e funcional
- Interface responsiva
- Integração completa com backend
""",
            "tempo_total": "35:00:00"
        },
        {
            "title": "Semana 6: Documentação e Entrega",
            "periodo": {"start": "2026-02-17", "end": "2026-02-20"},
            "descricao": """Finalização da documentação, vídeo de apresentação e preparação para entrega.

**Tarefas:**
- Documentação técnica completa
- Documentação de código
- Vídeo de apresentação (15 min)
- Preparação final do repositório
- Entrega final

**Entregáveis:**
- Documentação completa
- Vídeo gravado e editado
- Repositório preparado
- Sistema funcional e testado
""",
            "tempo_total": "25:00:00"
        }
    ]
    
    # Criar subitens (fases)
    print("📁 Criando subitens (fases do projeto)...")
    phase_ids = []
    
    for i, phase in enumerate(phases, 1):
        phase_card = await study.create_card(
            title=phase["title"],
            status=StudiesStatus.PARA_FAZER.value,
            categorias=["FIAP", "IA", "Projeto", "Fase"],
            prioridade=Priority.NORMAL.value,
            periodo=phase["periodo"],
            tempo_total=phase["tempo_total"],
            descricao=phase["descricao"],
            icon="📋",
            parent_item=project_id  # Vincular ao card principal
        )
        
        phase_id = phase_card['id']
        phase_url = f"https://www.notion.so/{phase_id.replace('-', '')}"
        phase_ids.append(phase_id)
        print(f"  ✅ Fase {i} criada: {phase_url}")
    
    print(f"\n✅ Todos os cards criados com sucesso!")
    print(f"\n📌 Card Principal: {project_url}")
    print(f"📁 Total de fases criadas: {len(phase_ids)}")
    
    return project_id, phase_ids


if __name__ == "__main__":
    try:
        project_id, phase_ids = asyncio.run(create_project_cards())
        print("\n🎉 Processo concluído com sucesso!")
    except Exception as e:
        print(f"\n❌ Erro ao criar cards: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

