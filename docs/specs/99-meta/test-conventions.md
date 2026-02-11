# Convenções de Testes Unitários

**Contexto para agentes e contributors.** Os testes devem **espelhar a estrutura de pastas do `app/`** (um arquivo de teste por módulo, na mesma hierarquia).

## Regra principal

Para cada módulo `app/<pasta>/<modulo>.py`:

```
tests/<pasta>/test_<modulo>.py
```

Ou, para submódulos: `app/<pasta>/<sub>/<modulo>.py` → `tests/<pasta>/<sub>/test_<modulo>.py`

## Estrutura esperada

| App | Tests |
|-----|-------|
| `app/core/config.py` | `tests/core/test_config.py` |
| `app/middlewares/exceptions_middleware.py` | `tests/middlewares/test_exceptions_middleware.py` |
| `app/threat_analysis/service.py` | `tests/threat_analysis/test_service.py` |
| `app/threat_analysis/controllers/threat_analysis_controller.py` | `tests/threat_analysis/controllers/test_threat_analysis_controller.py` |
| `app/threat_analysis/llm/fallback.py` | `tests/threat_analysis/llm/test_fallback.py` |

## O que NÃO fazer

- **Não** criar pasta `tests/` lotada de arquivos na raiz (`test_api.py`, `test_config.py`, etc. todos no mesmo nível)
- **Não** misturar testes de módulos diferentes em um único arquivo
- **Não** usar nomes genéricos sem caminho completo

## Exceção: smoke tests

Um único `tests/test_basic.py` na raiz é aceitável para imports e endpoint de health.

## Referência

Ver `.cursor/rules/test-structure.mdc` e estrutura em `threat-analyzer/tests/` e `threat-service/tests/`.
