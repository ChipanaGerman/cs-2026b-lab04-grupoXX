"""Diagrama generado exclusivamente desde eventos reales JSONL."""
import json
import sys
from pathlib import Path


def generar(archivo):
    p = Path(archivo)
    eventos = [json.loads(line) for line in p.read_text(encoding='utf-8').splitlines()]
    lines = ['sequenceDiagram', '    participant M as Modelo', '    participant C as Control', '    participant H as Herramientas']
    for e in eventos:
        estado = e['estado']
        if estado in {'OBSERVANDO', 'BLOQUEADO', 'CONTRATO_INVALIDO', 'FINALIZADO', 'LIMITE_ALCANZADO'}:
            label = f"{e['paso']}: {estado} {e.get('accion', '')}"
            lines += [f'    M->>C: {label}']
            if estado == 'OBSERVANDO':
                lines += [f"    C->>H: {e['accion']}", '    H-->>C: Observación registrada']
    p.with_suffix('.mmd').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    return p.with_suffix('.mmd')


if __name__ == '__main__':
    generar(sys.argv[1])
