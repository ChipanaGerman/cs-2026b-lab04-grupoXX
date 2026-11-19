"""Experimentos reproducibles: decisiones preparadas por Codex, herramientas reales.

Las respuestas de aprobación de este replay son fixtures automatizados; no son
aprobaciones de un integrante. Modo humano: orquestador.py sin --replay-aprobado.
"""
import json
import tempfile
from pathlib import Path
from .ejecutar import ROOT, preparar
from .agente.herramientas import Herramientas
from .agente.modelos import ModeloGrabado
from .agente.nucleo import Agente
from .agente.politica import Politica, aprobar_consola
from .agente.traza import generar

RUTA = 'src/pedidos/dominio.py'
ANTES_03 = '        self.disponible = False\n        pedido.marcar_preparando()'
DESPUES_03 = '        if not self.disponible:\n            raise ValueError("Repartidor ocupado")\n        pedido.marcar_preparando()\n        self.disponible = False'
ANTES_02 = '        if not plato.hay_stock(cantidad):\n            raise ValueError(f"Stock insuficiente para \'{plato.nombre}\'")\n        linea = LineaPedido('
INGENUO_02 = '        if not isinstance(cantidad, int) or cantidad <= 0:\n            raise ValueError("La cantidad debe ser un entero positivo")\n'+ANTES_02
CORRECTO_02 = '        if type(cantidad) is not int or cantidad <= 0:\n            raise ValueError("La cantidad debe ser un entero positivo")\n'+ANTES_02


def accion(nombre, **args):
    return {'pensamiento': 'Ejecutar '+nombre+' y observar antes de continuar.', 'accion': nombre, 'args': args}


def editar(antes, despues):
    return accion('editar_archivo', ruta=RUTA, antes=antes, despues=despues)


def final(texto):
    return {'pensamiento': 'Concluir según evidencia observada.', 'final': texto}


def ejecutar(nombre, raiz, decisiones, rol='ejecutor', aprobador=aprobar_consola, max_pasos=12):
    trayectoria = ROOT/f'agentes/trayectorias/{nombre}.json'
    trayectoria.parent.mkdir(parents=True, exist_ok=True)
    trayectoria.write_text(json.dumps({'origen': 'Decisiones preparadas por Codex para experimento reproducible', 'decisiones': decisiones}, ensure_ascii=False, indent=2), encoding='utf-8')
    herramientas = Herramientas(raiz)
    herramientas.original = (ROOT/'agentes/fixtures/dominio_base.py.txt').read_text(encoding='utf-8')
    agente = Agente(rol, ModeloGrabado(decisiones), herramientas, Politica(rol, max_pasos, aprobador), f'Experimento {nombre}. Resolver únicamente el issue indicado; no modificar pruebas.', ROOT/f'agentes/trazas/{nombre}.jsonl')
    resultado = agente.ejecutar()
    generar(agente.traza)
    (ROOT/f'agentes/evidencia/{nombre}.diff').write_text(agente.h.ver_cambios(), encoding='utf-8')
    return resultado, agente


def replay_aprobado(args):
    """Fixture de prueba, nunca se registra como aprobación humana."""
    return True


def issue03():
    with tempfile.TemporaryDirectory(prefix='picanteria-e4-') as temporal:
        raiz = Path(temporal)
        preparar(raiz)
        decisiones = [accion('leer_archivo', ruta='issues/ISSUE-03.md'),
                      accion('mapa_repo'), accion('buscar', texto='self.disponible'),
                      accion('anotar', texto='Hipótesis: asignar_pedido no consulta disponible. Editar solo la guardia; conservar estado al rechazar.'),
                      accion('leer_notas'), accion('ejecutar_pruebas', seleccion='03'),
                      editar(ANTES_03, DESPUES_03), accion('ejecutar_pruebas', seleccion='03'),
                      final('ISSUE-03 corregido. Dos pruebas pasan; nota persistente conserva la hipótesis. Aprobación automatizada de replay; requiere revisión humana.')]
        resultado, _ = ejecutar('issue03-notas', raiz, decisiones, aprobador=replay_aprobado)
        (ROOT/'agentes/evidencia/issue03-notas.md').write_text((raiz/'notas.md').read_text(encoding='utf-8'), encoding='utf-8')
        return resultado


if __name__ == '__main__':
    print(issue03())
