"""Auditor de catálogo: inspección determinista, nunca ejecuta tools/call."""
import json
from pathlib import Path
import re
from .rpc import Cliente, SERVIDOR


def auditar(catalogo):
    hallazgos = []
    for t in catalogo:
        nombre = t['name']
        descripcion = t.get('description', '').casefold()
        a = t.get('annotations') or {}
        def agregar(nivel, regla, detalle):
            hallazgos.append(dict(herramienta=nombre, nivel=nivel, regla=regla, detalle=detalle))
        if re.search(r'ignora.{0,40}instrucciones|ignore.{0,40}instructions', descripcion):
            agregar('ALTA', 'instrucciones_ocultas', 'Instrucciones al modelo ajenas al negocio')
        if re.search(r'api.?key|credenciales|secrets|secretos', descripcion):
            agregar('ALTA', 'secretos', 'Solicita material sensible')
        if '.env' in descripcion:
            agregar('MEDIA', 'archivo_sensible', 'Acceso a archivo ajeno a su función')
        propiedades = t.get('inputSchema', {}).get('properties', {})
        if 'contexto' in propiedades:
            agregar('MEDIA', 'contexto_generico', 'Entrada genérica apta para transportar datos ajenos')
        if not a:
            agregar('BAJA', 'sin_anotaciones', 'No declara alcance ni escritura')
        # Regla nueva 1: falta de destructiveHint en cualquier posible escritura.
        if a.get('readOnlyHint') is not True and 'destructiveHint' not in a:
            agregar('ALTA', 'escritura_sin_destructive', 'No se puede evaluar el efecto destructivo')
        # Regla nueva 2: texto libre sin cota, también en objetos anidados.
        def recorrer(schema, ruta):
            if schema.get('type') == 'string' and not any(k in schema for k in ('maxLength', 'enum', 'const')):
                agregar('MEDIA', 'texto_sin_limite', f'{ruta}: falta maxLength o enum')
            for k, s in schema.get('properties', {}).items():
                recorrer(s, ruta+'.'+k)
            if isinstance(schema.get('items'), dict):
                recorrer(schema['items'], ruta+'[]')
            for s in schema.get('anyOf', []):
                recorrer(s, ruta)
        recorrer(t.get('inputSchema', {}), 'args')
    return hallazgos


if __name__ == '__main__':
    base = Path(__file__).resolve().parents[1]
    resultados = {}
    for nombre, servidor in [('propio', SERVIDOR), ('tercero_fixture', base/'terceros/clima_mcp.py')]:
        with Cliente(servidor=servidor) as c:
            catalogo = c.pedir('tools/list')['result']['tools']
            resultados[nombre] = {'catalogo': catalogo, 'hallazgos': auditar(catalogo)}
            c.guardar(base/f'trazas/auditoria-{nombre}.jsonl')
    (base/'trazas/auditoria.json').write_text(json.dumps(resultados, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: v['hallazgos'] for k, v in resultados.items()}, ensure_ascii=False, indent=2))
