# threat-modeling-shared

Mini biblioteca padronizada para os backends do Threat Modeling AI (threat-analyzer e threat-service).

## O que fornece

| Módulo | Descrição |
|--------|-----------|
| **config** | `BaseSettings` (Pydantic), `env_file_paths`, `parse_cors_origins` |
| **logging** | `setup_logging`, `get_logger` |
| **middleware** | `CatchExceptionsMiddleware`, `LoggingMiddleware` |
| **routers** | `create_health_router` (/health, /health/ready, /health/live) |
| **create_app** | Factory FastAPI padronizada com CORS, middlewares, health |

## Uso — criar app

```python
from threat_modeling_shared import create_app

app = create_app(
    title="Meu Serviço",
    description="...",
    version="1.0.0",
    routers=[(my_router, {"prefix": "/api/v1"})],
    settings=my_settings,
    lifespan=my_lifespan,
    check_database=True,
    db_check=lambda: check_db(),
)
```

## Uso — config estendendo BaseSettings

```python
from threat_modeling_shared.config import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Meu Serviço"
    # Herda: app_version, debug, log_level, cors_*, env_file_paths
    # Adicione campos específicos do serviço
    database_url: str = "postgresql://..."
```

## Estrutura

- **threat-analyzer** e **threat-service** usam `create_app` + `BaseSettings`
- Config em `app/core/config.py` estende `BaseSettings`
- Middlewares e health vêm da shared — nada duplicado
