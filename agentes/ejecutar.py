"""CLI: python -m agentes.ejecutar --issue 01 [--replay archivo.json]."""
import argparse
import json
import shutil
import tempfile
from pathlib import Path
from .agente.herramientas import Herramientas
from .agente.modelos import ModeloInteractivo, ModeloGrabado
from .agente.nucleo import Agente
from .agente.politica import Politica
from .agente.traza import generar

ROOT = Path(__file__).resolve().parents[1]


def preparar(raiz):
    for nombre in ('src', 'tests', 'issues'):
        shutil.copytree(ROOT/nombre, raiz/nombre, ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copy(ROOT/'pytest.ini', raiz/'pytest.ini')
    (raiz/'src/pedidos/dominio.py').write_text((ROOT/'agentes/fixtures/dominio_base.py.txt').read_text(encoding='utf-8'), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--issue', choices=['01', '02', '03'], required=True)
    parser.add_argument('--replay')
    parser.add_argument('--salida', default='issue01-interactivo')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='picanteria-lab10-') as temporal:
        raiz = Path(temporal)
        preparar(raiz)
        modelo = ModeloGrabado(json.loads(Path(args.replay).read_text(encoding='utf-8'))['decisiones']) if args.replay else ModeloInteractivo(ROOT/f'agentes/trayectorias/{args.salida}.json')
        traza = ROOT/f'agentes/trazas/{args.salida}.jsonl'
        agente = Agente('ejecutor', modelo, Herramientas(raiz), Politica(), f'Resolver issues/ISSUE-{args.issue}.md. Lee, reproduce, edita y verifica la prueba correspondiente. No cambies tests.', traza)
        print(agente.ejecutar())
        generar(traza)
        destino = ROOT/f'agentes/evidencia/{args.salida}.diff'
        destino.write_text(agente.h.ver_cambios(), encoding='utf-8')
        (ROOT/f'agentes/evidencia/{args.salida}-dominio.py.txt').write_text((raiz/'src/pedidos/dominio.py').read_text(encoding='utf-8'), encoding='utf-8')


if __name__ == '__main__':
    main()
