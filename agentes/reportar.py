"""Métricas y diagramas derivados de las trazas; no inventa resultados."""
import json
import subprocess
from pathlib import Path
from .ejecutar import ROOT


def metricas(archivo):
    eventos = [json.loads(x) for x in Path(archivo).read_text(encoding='utf-8').splitlines()]
    acciones = [e for e in eventos if e['estado'] in {'OBSERVANDO', 'BLOQUEADO'}]
    return dict(pasos=sum(e['estado'] == 'DECIDIENDO' for e in eventos),
                acciones=len(acciones), bloqueadas=sum(e['estado'] == 'BLOQUEADO' for e in eventos),
                invalidas=sum(e['estado'] == 'CONTRATO_INVALIDO' for e in eventos),
                herramientas=sorted({e['accion'] for e in acciones}),
                contexto=eventos[-1]['contexto_final'])


def tabla():
    filas = ['| Ejecución | Pasos | Rondas | Acciones | Contratos rechazados | Bloqueadas | Contexto final (car.) |',
             '|---|---:|---:|---:|---:|---:|---:|']
    datos = {}
    for p in sorted((ROOT/'agentes/trazas').glob('*.jsonl')):
        if p.stem.startswith('issue'):
            m = metricas(p)
            datos[p.stem] = m
            ronda = 2 if p.stem.endswith('r2') else 1
            filas.append(f"| {p.stem} | {m['pasos']} | {ronda} | {m['acciones']} | {m['invalidas']} | {m['bloqueadas']} | {m['contexto']} |")
    return '\n'.join(filas), datos


def diagramas():
    for p in (ROOT/'agentes/trazas').glob('*.jsonl'):
        eventos = [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines()]
        lineas = ['@startuml', 'title '+p.stem, 'participant Modelo', 'participant Control', 'participant Herramientas']
        for e in eventos:
            if e['estado'] in {'OBSERVANDO', 'BLOQUEADO', 'CONTRATO_INVALIDO', 'FINALIZADO', 'LIMITE_ALCANZADO'}:
                texto = f"{e['paso']}: {e['estado']} {e.get('accion', '')}"
                lineas += ['Modelo -> Control : '+texto]
                if e['estado'] == 'OBSERVANDO':
                    lineas += ['Control -> Herramientas : '+e['accion'], 'Herramientas --> Control : resultado registrado']
        p.with_suffix('.puml').write_text('\n'.join(lineas+['@enduml'])+'\n', encoding='utf-8')
    archivos = [str(p) for p in (ROOT/'agentes/trazas').glob('*.puml')]+[str(ROOT/'agentes/diseno/estados.puml')]
    subprocess.run(['java', '-jar', str(ROOT/'plantuml.jar'), '-charset', 'UTF-8', '-tpng', *archivos], check=True, timeout=60)


def main():
    t, datos = tabla()
    multi = [v for k, v in datos.items() if k.startswith('issue02-') and k != 'issue02-unico']
    unico = datos['issue02-unico']
    detalle = '\n'.join(f"| {k} | {', '.join(v['herramientas'])} |" for k, v in datos.items())
    texto = '# E7. Observación de ejecuciones reales\n\n'+t+'\n\n'
    texto += ('Pasos cuenta decisiones solicitadas, incluida la final. Acciones cuenta llamadas permitidas o bloqueadas; '
              'los rechazos de contrato se cuentan por separado. Rondas indica el número de ronda de esa traza; '
              'no debe sumarse entre actores de una misma ronda. Contexto es la longitud JSON del historial final, '
              'incluido catálogo y observaciones, sin convertir caracteres en tokens ni estimar dinero.\n\n')
    texto += '| Ejecución | Herramientas intentadas |\n|---|---|\n'+detalle+'\n\n'
    texto += '## E5. Comparación agregada\n\n'
    texto += f"Agente único: {unico['acciones']} acciones, {unico['contexto']} caracteres finales, una ronda. "
    texto += f"Gestor + actor-crítico: {sum(x['acciones'] for x in multi)} acciones, {sum(x['contexto'] for x in multi)} caracteres finales acumulados entre contextos y dos rondas. "
    texto += f"Bloqueos: {sum(x['bloqueadas'] for x in multi)}. Sumar contextos finales mide volumen acumulado de sesiones, no tokens facturados ni todas las llamadas.\n\n"
    texto += ('El crítico detectó que `isinstance(True, int)` acepta una cantidad booleana.  \n'
              'El agente único también encontró el fallo con las mismas pruebas y llegó al mismo parche.  \n'
              'El esquema actor-crítico necesitó dos rondas y un contexto separado para cada rol.  \n'
              'La separación bloqueó un intento de escritura del revisor.  \n'
              'No apareció un defecto exclusivo del crítico que las pruebas del agente único omitieran.  \n'
              'Para estos issues pequeños conviene el agente único con tests y revisión humana.  \n'
              'Se reservaría actor-crítico para cambios de mayor riesgo: esa decisión respeta parsimonia (sección 1.7).\n\n')
    a, b = datos['issue01-interactivo'], datos['issue03-notas']
    texto += f"## E4. Efecto observado\n\nE2: {a['pasos']} pasos y {a['contexto']} caracteres. E4: {b['pasos']} pasos y {b['contexto']} caracteres. "
    texto += ('Las notas agregan llamadas; el mapa evita leer todo el dominio. Issues distintos y catálogos distintos '
              'impiden atribuir causalmente el cambio de contexto a una sola herramienta.\n\n')
    texto += '## Trayectoria del issue 3\n\n![Trayectoria generada desde JSONL](trazas/issue03-notas.png)\n\n'
    texto += ('## Procedencia y límites\n\nE2 usa ModeloInteractivo con respuestas de Codex introducidas por consola. '
              'E4/E5 usan decisiones preparadas y replay, no inferencias autónomas nuevas. '
              'Las herramientas y pruebas se ejecutaron realmente. Los intentos inválidos del revisor son casos '
              'adversarios deliberados, no un fallo espontáneo de un proveedor. No hubo credenciales ni datos reales. '
              'Las aprobaciones automatizadas no acreditan una intervención humana. Ver delegacion.md.\n')
    (ROOT/'agentes/observacion.md').write_text(texto, encoding='utf-8')
    (ROOT/'agentes/evidencia/metricas.json').write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding='utf-8')
    diagramas()
    print(t)


if __name__ == '__main__':
    main()
