#!/usr/bin/env python3
"""
Limpa todas as análises no threat-service e envia as imagens de test-assets para análise.

Requer a stack rodando (make run): threat-service :8000, celery, threat-analyzer.
Uso (na raiz do projeto):
  make run   # em outro terminal
  PYTHONPATH=. python scripts/clear_and_run_test_analyses.py

  # Ou com URL do serviço:
  THREAT_SERVICE_URL=http://localhost:8000 PYTHONPATH=. python scripts/clear_and_run_test_analyses.py
"""

import os
import sys
import time
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent
TEST_ASSETS = _PROJECT_ROOT / "test-assets"

DEFAULT_SERVICE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1/analyses"


def _client():
    try:
        import httpx

        return httpx
    except ImportError:
        print("Instale httpx: pip install httpx", file=sys.stderr)
        sys.exit(1)


def clear_all_analyses(base_url: str) -> int:
    """Lista todas as análises e deleta uma a uma. Retorna quantidade removida."""
    httpx = _client()
    url = f"{base_url.rstrip('/')}{API_PREFIX}"
    deleted = 0
    page = 1
    size = 50
    while True:
        with httpx.Client(timeout=30.0) as client:
            r = client.get(url, params={"page": page, "size": size})
        r.raise_for_status()
        data = r.json()
        items = data.get("items", [])
        if not items:
            break
        for item in items:
            aid = item.get("id")
            if not aid:
                continue
            with httpx.Client(timeout=30.0) as client:
                dr = client.delete(f"{url}/{aid}")
            if dr.status_code in (200, 204):
                deleted += 1
                print(f"  Removida análise {item.get('code', aid)}")
        if len(items) < size:
            break
        page += 1
    return deleted


def create_analysis(base_url: str, image_path: Path) -> dict | None:
    """POST da imagem e retorna o JSON da criação (id, code, status)."""
    httpx = _client()
    url = f"{base_url.rstrip('/')}{API_PREFIX}"
    suffix = image_path.suffix.lower()
    content_type = (
        "image/png"
        if suffix == ".png"
        else "image/jpeg"
        if suffix in (".jpg", ".jpeg")
        else "image/webp"
        if suffix == ".webp"
        else "image/gif"
        if suffix == ".gif"
        else "image/png"
    )
    with open(image_path, "rb") as f:
        content = f.read()
    with httpx.Client(timeout=60.0) as client:
        r = client.post(
            url,
            files={"file": (image_path.name, content, content_type)},
        )
    r.raise_for_status()
    return r.json()


def get_analysis(base_url: str, analysis_id: str) -> dict | None:
    """GET análise por ID."""
    httpx = _client()
    url = f"{base_url.rstrip('/')}{API_PREFIX}/{analysis_id}"
    with httpx.Client(timeout=30.0) as client:
        r = client.get(url)
    if r.status_code != 200:
        return None
    return r.json()


def wait_for_done(
    base_url: str, analysis_id: str, code: str, max_wait_sec: int = 600
) -> bool:
    """Aguarda status ANALISADO ou FALHOU. Retorna True se ANALISADO."""
    start = time.time()
    while (time.time() - start) < max_wait_sec:
        data = get_analysis(base_url, analysis_id)
        if not data:
            time.sleep(5)
            continue
        status = data.get("status")
        if status == "ANALISADO":
            print(
                f"    {code}: concluído (threats: {len((data.get('result') or {}).get('threats', []))})"
            )
            return True
        if status == "FALHOU":
            print(f"    {code}: falhou - {data.get('error_message', '')[:200]}")
            return False
        time.sleep(8)
    print(f"    {code}: timeout")
    return False


def main() -> int:
    base_url = os.environ.get("THREAT_SERVICE_URL", DEFAULT_SERVICE_URL)

    print("==> Limpando análises existentes...")
    try:
        n = clear_all_analyses(base_url)
        print(f"    {n} análise(s) removida(s).\n")
    except Exception as e:
        print(f"    Erro ao limpar: {e}", file=sys.stderr)
        return 1

    images = [
        TEST_ASSETS / "diagrama-aws.png",
        TEST_ASSETS / "diagrama-azure.png",
    ]
    for path in images:
        if not path.exists():
            print(f"Arquivo não encontrado: {path}", file=sys.stderr)
            continue

        print(f"==> Enviando {path.name} para {base_url}{API_PREFIX}")
        try:
            created = create_analysis(base_url, path)
        except Exception as e:
            print(f"    Erro: {e}", file=sys.stderr)
            continue
        aid = created.get("id")
        code = created.get("code", aid)
        print(f"    Criada {code} (id: {aid})")
        wait_for_done(base_url, aid, code)
        print()

    print("Concluído.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
