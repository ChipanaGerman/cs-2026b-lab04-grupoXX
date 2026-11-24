"""Gestor y actor-crítico, máximo dos rondas. Sin autoaprobación por defecto.

python -m agentes.orquestador --replay-aprobado   # experimento automático
python -m agentes.orquestador                     # ediciones aprobadas por consola
"""
import argparse
import json
import tempfile
from pathlib import Path
from .ejecutar import ROOT, preparar
from .experimentos import (RUTA, ANTES_02, INGENUO_02, CORRECTO_02, accion,
                            editar, final, ejecutar, replay_aprobado)
from .agente.politica import aprobar_consola


def secuencia_unico():
    return [accion('leer_archivo', ruta='issues/ISSUE-02.md'),
            accion('ejecutar_pruebas', seleccion='02'),
            accion('leer_archivo', ruta=RUTA), editar(ANTES_02, INGENUO_02),
            accion('ejecutar_pruebas', seleccion='02'),
            editar('not isinstance(cantidad, int)', 'type(cantidad) is not int'),
            accion('ejecutar_pruebas', seleccion='02'),
            final('ISSUE-02 resuelto: bool hereda de int; usar type exacto. Siete casos verdes.')]


def aprobado(agente):
    """Un crítico no puede aprobar sin una prueba observada exitosa."""
    pruebas = [e for e in agente.eventos if e.get('accion') == 'ejecutar_pruebas' and e['estado'] == 'OBSERVANDO']
    hay_prueba = bool(pruebas) and pruebas[-1].get('observacion', '').startswith('EXIT=0\n')
    return hay_prueba and any(e['estado'] == 'FINALIZADO' and e['texto'].startswith('APROBADO:') for e in agente.eventos)


def comparar(aprobador=aprobar_consola):
    resultados = {}
    with tempfile.TemporaryDirectory(prefix='picanteria-unico-') as t:
        raiz = Path(t)
        preparar(raiz)
        resultado, agente = ejecutar('issue02-unico', raiz, secuencia_unico(), aprobador=aprobador)
        pruebas = [e for e in agente.eventos if e['estado'] == 'OBSERVANDO' and e.get('accion') == 'ejecutar_pruebas']
        if not pruebas or not pruebas[-1]['observacion'].startswith('EXIT=0\n'):
            resultado = 'NO RESUELTO: aprobación rechazada o prueba fallida; requiere intervención humana'
        resultados['unico'] = resultado
        unico_final = (raiz/RUTA).read_text(encoding='utf-8')
    with tempfile.TemporaryDirectory(prefix='picanteria-multi-') as t:
        raiz = Path(t)
        preparar(raiz)
        plan, _ = ejecutar('issue02-planificador', raiz, [accion('leer_archivo', ruta='issues/ISSUE-02.md'), final('PLAN: reproducir; validar entero positivo antes del stock; revisar bool, tipo y mutación; verificar pytest; humano aprueba PR.')], rol='planificador', max_pasos=4)
        retro = ''
        for ronda in (1, 2):
            decisiones = ([accion('leer_archivo', ruta=RUTA), editar(ANTES_02, INGENUO_02), final('Propuesta de cantidad positiva; falta verificación del crítico.')]
                          if ronda == 1 else
                          [editar('not isinstance(cantidad, int)', 'type(cantidad) is not int'), accion('ejecutar_pruebas', seleccion='02'), final('Corregida aceptación de bool; pruebas verdes.')])
            # Plan y crítica forman parte de la entrada del actor, no mensajes decorativos.
            from .agente.herramientas import Herramientas
            from .agente.modelos import ModeloGrabado
            from .agente.nucleo import Agente
            from .agente.politica import Politica
            from .agente.traza import generar
            nombre = f'issue02-actor-r{ronda}'
            (ROOT/f'agentes/trayectorias/{nombre}.json').write_text(json.dumps({'origen': 'Decisiones preparadas por Codex', 'decisiones': decisiones}, ensure_ascii=False, indent=2), encoding='utf-8')
            actor = Agente('ejecutor', ModeloGrabado(decisiones), Herramientas(raiz), Politica('ejecutor', 12, aprobador), f'{plan}\n{retro}', ROOT/f'agentes/trazas/{nombre}.jsonl')
            actor.ejecutar()
            generar(actor.traza)
            veredicto = 'CAMBIOS SOLICITADOS: bool es subtipo de int. True sigue aceptado; corregir a type(cantidad) is int.' if ronda == 1 else 'APROBADO: siete casos pasan; no se tocaron tests. Pendiente aprobación humana del PR.'
            # Intento de escritura del revisor debe bloquearse sin ejecutar ni pedir aprobación.
            revision = ([editar('return 0', 'return 1')] if ronda == 1 else []) + [accion('ver_cambios'), accion('ejecutar_pruebas', seleccion='02'), final(veredicto)]
            retro, critico = ejecutar(f'issue02-critico-r{ronda}', raiz, revision, rol='revisor', max_pasos=8)
            if aprobado(critico):
                resultados['actor_critico'] = retro
                break
            if ronda == 2:
                resultados['actor_critico'] = 'NO APROBADO: requiere intervención humana'
        multi_final = (raiz/RUTA).read_text(encoding='utf-8')
        if resultados['actor_critico'].startswith('APROBADO:') and not resultado.startswith('NO RESUELTO'):
            assert multi_final == unico_final, 'Los experimentos aprobados deben llegar al mismo parche'
        (ROOT/'agentes/evidencia/issue02-final-dominio.py.txt').write_text(multi_final, encoding='utf-8')
    return resultados


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--replay-aprobado', action='store_true', help='Fixture automatizado, no aprobación humana')
    args = parser.parse_args()
    print(json.dumps(comparar(replay_aprobado if args.replay_aprobado else aprobar_consola), ensure_ascii=False, indent=2))
