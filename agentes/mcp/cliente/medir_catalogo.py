"""Guarda catálogos reales para comparar descripciones antes/después."""
import argparse
import json
from pathlib import Path
from .rpc import Cliente
from .traza_mcp import costo

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('fase', choices=['antes', 'despues'])
    a = p.parse_args()
    base = Path(__file__).resolve().parents[1]/'trazas'
    with Cliente() as c:
        catalogo = c.pedir('tools/list')['result']['tools']
        (base/f'catalogo-{a.fase}.json').write_text(json.dumps(catalogo, ensure_ascii=False, indent=2), encoding='utf-8')
        (base/f'costo-{a.fase}.json').write_text(json.dumps(costo(catalogo), ensure_ascii=False, indent=2), encoding='utf-8')
        print(costo(catalogo))
