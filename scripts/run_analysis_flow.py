#!/usr/bin/env python3
"""
Fluxo de teste de analise: envia imagens de diagrama ao threat-analyzer e exibe a resposta.

Requer o threat-analyzer rodando (ex.: make run). Por padrao usa http://localhost:8001.

Uso (na raiz do projeto):
  make run   # em outro terminal
  make test-analysis-flow IMAGE=caminho/para/diagrama.png

  # Ou chamando o script diretamente (uma ou mais imagens):
  PYTHONPATH=. python scripts/run_analysis_flow.py --image path/to/diagram.png
  PYTHONPATH=. python scripts/run_analysis_flow.py --base-url http://localhost:8001 --image img1.png --image img2.png
"""

import argparse
import json
import sys
from pathlib import Path

# Project root: scripts/run_analysis_flow.py -> scripts -> project root
_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent

DEFAULT_BASE_URL = "http://localhost:8001"
ANALYZE_PATH = "/api/v1/threat-model/analyze"


def analyze_image(base_url: str, image_path: Path) -> dict | None:
    """Envia uma imagem para POST /api/v1/threat-model/analyze e retorna o JSON da resposta."""
    try:
        import httpx
    except ImportError:
        print("Instale httpx: pip install httpx", file=sys.stderr)
        return None

    url = f"{base_url.rstrip('/')}{ANALYZE_PATH}"
    path = image_path.resolve()
    if not path.exists():
        print(f"Arquivo nao encontrado: {path}", file=sys.stderr)
        return None

    with open(path, "rb") as f:
        content = f.read()
    suffix = path.suffix.lower()
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

    try:
        with httpx.Client(timeout=120.0) as client:
            r = client.post(
                url,
                files={"file": (path.name, content, content_type)},
                data={},
            )
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        print(f"Request falhou: {e}", file=sys.stderr)
        try:
            print(e.response.text[:1000], file=sys.stderr)
        except Exception:
            pass
        return None
    except httpx.RequestError as e:
        print(f"Request falhou: {e}", file=sys.stderr)
        return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Testa o fluxo de analise enviando imagens ao threat-analyzer."
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"URL base do threat-analyzer (default: {DEFAULT_BASE_URL}).",
    )
    parser.add_argument(
        "--image",
        dest="images",
        action="append",
        type=Path,
        default=None,
        help="Caminho para imagem de diagrama (pode repetir). Obrigatorio ao menos um.",
    )
    parser.add_argument(
        "--save",
        type=Path,
        default=None,
        help="Salvar ultima resposta JSON neste arquivo.",
    )
    args = parser.parse_args()

    images = args.images if args.images else []
    if not images:
        print("Passe ao menos uma imagem com --image <caminho>.", file=sys.stderr)
        return 1

    images = [p if p.is_absolute() else _PROJECT_ROOT / p for p in images]
    last_response = None
    for img_path in images:
        path = img_path.resolve()
        print(f"==> Enviando {path.name} para {args.base_url}{ANALYZE_PATH}")
        resp = analyze_image(args.base_url, path)
        if resp is None:
            print("    Falha.\n")
            continue
        last_response = resp
        print("    Status: OK")
        print(f"    model_used: {resp.get('model_used', 'N/A')}")
        print(f"    components: {len(resp.get('components', []))}")
        print(f"    connections: {len(resp.get('connections', []))}")
        print(f"    threats: {len(resp.get('threats', []))}")
        print(
            f"    risk_level: {resp.get('risk_level', 'N/A')} (score: {resp.get('risk_score', 'N/A')})"
        )
        print(f"    processing_time: {resp.get('processing_time', 'N/A')}s")
        print()

    if args.save and last_response is not None:
        args.save.parent.mkdir(parents=True, exist_ok=True)
        with open(args.save, "w", encoding="utf-8") as f:
            json.dump(last_response, f, ensure_ascii=False, indent=2)
        print(f"Resposta salva em {args.save}")

    return 0 if last_response is not None else 1


if __name__ == "__main__":
    sys.exit(main())
