from pathlib import Path
import pytest
from agentes.agente.herramientas import Herramientas


def test_mapa_no_ejecuta_y_muestra_firmas(tmp_path):
    p = tmp_path/'src/pedidos/dominio.py'
    p.parent.mkdir(parents=True)
    p.write_text('raise RuntimeError("no importar")\ndef asignar(pedido, disponible=True):\n    pass\n', encoding='utf-8')
    h = Herramientas(tmp_path)
    assert 'asignar(pedido, disponible=True)' in h.mapa_repo()
    assert 'src/pedidos/dominio.py:2' in h.mapa_repo()


def test_notas_persisten_entre_instancias_y_aislan_sandboxes(tmp_path):
    for nombre in ('a', 'b'):
        p = tmp_path/nombre/'src/pedidos/dominio.py'
        p.parent.mkdir(parents=True)
        p.write_text('', encoding='utf-8')
    h = Herramientas(tmp_path/'a')
    h.anotar('Revisado asignar_pedido: falta guardia disponible.')
    assert 'falta guardia' in Herramientas(tmp_path/'a').leer_notas()
    assert 'falta guardia' not in Herramientas(tmp_path/'b').leer_notas()
    with pytest.raises(ValueError):
        h.anotar(' ')
    with pytest.raises(ValueError):
        h.anotar('x'*2001)
