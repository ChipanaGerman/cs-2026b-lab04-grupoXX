from types import SimpleNamespace
from agentes.orquestador import aprobado


def test_critico_no_aprueba_sin_prueba_verde():
    final = {'estado': 'FINALIZADO', 'texto': 'APROBADO: listo'}
    assert not aprobado(SimpleNamespace(eventos=[final]))
    rojo = {'estado': 'OBSERVANDO', 'accion': 'ejecutar_pruebas', 'observacion': 'EXIT=1\nfalló'}
    verde = {**rojo, 'observacion': 'EXIT=0\n7 passed'}
    assert aprobado(SimpleNamespace(eventos=[verde, final]))
    assert not aprobado(SimpleNamespace(eventos=[verde, rojo, final]))
