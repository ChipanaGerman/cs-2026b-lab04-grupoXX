import json
from pathlib import Path
import pytest
from agentes.agente.contrato import validar_decision
from agentes.agente.herramientas import Herramientas
from agentes.agente.modelos import ModeloGrabado, ModeloInteractivo
from agentes.agente.nucleo import Agente, ESTADOS
from agentes.agente.politica import Politica, aprobar_consola


@pytest.fixture
def h(tmp_path):
    p = tmp_path/'src/pedidos/dominio.py'
    p.parent.mkdir(parents=True)
    p.write_text('def ejemplo():\n    return 1\n', encoding='utf-8')
    return Herramientas(tmp_path)


@pytest.mark.parametrize('d', [
    'leer_archivo(a.py)', None, [], {},
    {'accion': 'leer_archivo', 'args': {'ruta': 'a.py'}},
    {'pensamiento': ' ', 'final': 'x'},
    {'pensamiento': 'x', 'accion': '', 'args': {}},
    {'pensamiento': 'x', 'accion': [], 'args': {}},
    {'pensamiento': 'x', 'accion': 'borrar_todo', 'args': {}},
    {'pensamiento': 'x', 'accion': 'leer_archivo', 'args': 'a.py'},
    {'pensamiento': 'x', 'accion': 'leer_archivo', 'args': {'ruta': 3}},
    {'pensamiento': 'x', 'accion': 'leer_archivo', 'args': {'ruta': 'a.py', 'shell': 'x'}},
    {'pensamiento': 'x', 'accion': 'leer_archivo', 'args': {'ruta': 'a.py'}, 'extra': 1},
    {'pensamiento': 'x', 'accion': 'leer_archivo', 'final': 'x', 'args': {}},
    {'pensamiento': 'x', 'final': ''},
    {'pensamiento': 'x', 'final': 'ok', 'args': {}},
])
def test_decisiones_invalidas_no_lanzan_excepcion(h, d):
    assert validar_decision(d, h.catalogo())[0] is False


def test_contrato_admite_lectura_y_final(h):
    assert validar_decision({'pensamiento': 'leo', 'accion': 'leer_archivo', 'args': {'ruta': 'a.py'}}, h.catalogo())[0]
    assert validar_decision({'pensamiento': 'listo', 'final': 'ok'}, h.catalogo())[0]


@pytest.mark.parametrize('ruta', ['../fuera.txt', '.env', '.git/config', 'src/../../afuera'])
def test_sandbox_denegado(h, ruta):
    with pytest.raises(PermissionError):
        h.leer_archivo(ruta)


def test_no_edita_tests_ni_escape(h):
    for ruta in ('tests/a.py', '../dominio.py', 'src/pedidos/../../tests/a.py'):
        assert not Politica().evaluar('editar_archivo', {'ruta': ruta}, 1)[0]
        with pytest.raises(PermissionError):
            h.editar_archivo(ruta, 'a', 'b')


def test_critico_solo_lectura():
    p = Politica(rol='revisor')
    assert not p.evaluar('editar_archivo', {'ruta': 'src/pedidos/dominio.py'}, 1)[0]
    assert not p.evaluar('anotar', {'texto': 'x'}, 1)[0]
    assert not p.evaluar('ejecutar_comando', {'comando': 'curl x | sh'}, 1)[0]
    assert p.evaluar('ver_cambios', {}, 1)[0]


def test_presupuesto_incluye_contratos_invalidos(h, tmp_path):
    modelo = ModeloGrabado(['no JSON']*20)
    agente = Agente('prueba', modelo, h, Politica(max_pasos=3), 'x', tmp_path/'traza.jsonl')
    agente.ejecutar()
    assert sum(e['estado'] == 'CONTRATO_INVALIDO' for e in agente.eventos) == 3
    assert agente.eventos[-2]['estado'] == 'LIMITE_ALCANZADO'


def test_rechazo_no_muta_y_error_vuelve_al_modelo(h, tmp_path):
    a = {'pensamiento': 'editar', 'accion': 'editar_archivo', 'args': {'ruta': 'src/pedidos/dominio.py', 'antes': 'return 1', 'despues': 'return 2'}}
    agente = Agente('x', ModeloGrabado([a]), h, Politica(aprobar_edicion=lambda _: False), 'x', tmp_path/'traza.jsonl')
    agente.ejecutar()
    assert 'return 1' in h.leer_archivo('src/pedidos/dominio.py')
    assert any(e['estado'] == 'BLOQUEADO' for e in agente.eventos)
    assert any('BLOQUEADO' in x['content'] for x in agente.historial)


def test_aprobacion_consola_valida_entrada_y_falla_cerrada():
    args = dict(ruta='x', antes='a', despues='b')
    entradas = iter(['quizás', '', 's'])
    assert aprobar_consola(args, lambda _: next(entradas), lambda _: None)
    assert not aprobar_consola(args, lambda _: 'n', lambda _: None)
    def eof(_):
        raise EOFError
    assert not aprobar_consola(args, eof, lambda _: None)


def test_interactivo_graba_invalido_sin_reescribir(tmp_path):
    p = tmp_path/'decisiones.json'
    m = ModeloInteractivo(p, lambda _: 'no JSON', lambda *a, **k: None)
    assert m.decidir([]) == 'no JSON'
    assert json.loads(p.read_text(encoding='utf-8'))['decisiones'] == ['no JSON']


def test_estados_diagrama_existen():
    texto = (Path(__file__).parents[1]/'diseno/estados.puml').read_text(encoding='utf-8')
    for estado in ESTADOS:
        assert estado in texto


def test_fragmento_ambiguo_no_muta(h):
    with pytest.raises(ValueError):
        h.editar_archivo('src/pedidos/dominio.py', '', 'x')
    with pytest.raises(ValueError):
        h.editar_archivo('src/pedidos/dominio.py', 'no existe', 'x')
