"""Genera secuencia y métricas exclusivamente desde los bytes capturados."""
import argparse
import json
import math
from pathlib import Path
import statistics


def analizar(ruta):
    eventos = [json.loads(l) for l in Path(ruta).read_text(encoding='utf-8').splitlines()]
    pendientes, latencias, lineas = {}, {}, ['sequenceDiagram', '    participant C as Agente / cliente', '    participant S as Picantería MCP', '    actor H as Humano']
    errores = 0
    for e in eventos:
        m = e['mensaje']
        if e['direccion'] == 'cliente->servidor':
            pendientes[m['id']] = m
            nombre = m['method']
            if nombre == 'tools/call':
                nombre += ': '+m['params']['name']
            lineas.append(f'    C->>S: id={m["id"]} {nombre}')
        else:
            req = pendientes[m['id']]
            latencias.setdefault(req['method'], []).append(e['latencia_ms'])
            resultado = m.get('result', {})
            tipo = 'error JSON-RPC' if 'error' in m else 'isError' if resultado.get('isError') else resultado.get('resultType', 'complete')
            errores += int('error' in m or resultado.get('isError', False))
            lineas.append(f'    S-->>C: id={m["id"]} {tipo} ({e["bytes"]} bytes)')
            if tipo == 'input_required':
                lineas.extend(['    C->>H: ¿Crear este reclamo?', '    H-->>C: Aprobación explícita registrada'])
    metricas = {'origen': str(ruta), 'mensajes': len(eventos), 'bytes': sum(e['bytes'] for e in eventos),
                'errores': errores, 'latencia_ms_por_metodo': {
                    k: {'n': len(v), 'media': round(statistics.mean(v), 3), 'min': min(v), 'max': max(v)}
                    for k, v in latencias.items()}}
    return metricas, '\n'.join(lineas)+'\n'


def costo(catalogo):
    raw = json.dumps(catalogo, ensure_ascii=False, separators=(',', ':'))
    return {'caracteres': len(raw), 'bytes_utf8': len(raw.encode('utf-8')),
            'tokens_estimados': math.ceil(len(raw)/4), 'metodo': 'ceil(caracteres JSON compacto / 4); estimación, no tokenizer del host'}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('traza', nargs='?', default='agentes/mcp/trazas/negocio.jsonl')
    args = p.parse_args()
    ruta = Path(args.traza)
    metricas, secuencia = analizar(ruta)
    ruta.with_suffix('.metricas.json').write_text(json.dumps(metricas, ensure_ascii=False, indent=2), encoding='utf-8')
    ruta.with_suffix('.mmd').write_text(secuencia, encoding='utf-8')
    print(json.dumps(metricas, ensure_ascii=False, indent=2))
