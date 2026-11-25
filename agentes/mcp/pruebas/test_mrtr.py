"""Reto B: confirmación multivuelta real y pruebas de abuso."""
import pytest
from agentes.mcp.cliente.rpc import Cliente

ARGS = {'pedido_id': '00000000-0000-0000-0000-000000000001',
        'descripcion': 'Pedido cancelado sin explicación; solicito revisión.'}


@pytest.fixture
def c(tmp_path):
    with Cliente(entorno={'PICANTERIA_RECLAMOS_DIR': str(tmp_path)}) as cliente:
        cliente.carpeta = tmp_path
        yield cliente


def continuar(c, inicial, action='accept', confirmar=True, args=None):
    return c.llamar('registrar_reclamo', args or ARGS,
        requestState=inicial['result']['requestState'],
        inputResponses={'confirmar': {'action': action, 'content': {'confirmar': confirmar}}})


def test_input_required_antes_de_escribir(c):
    r = c.llamar('registrar_reclamo', ARGS)
    assert r['result']['resultType'] == 'input_required'
    assert r['result']['inputRequests']['confirmar']['method'] == 'elicitation/create'
    assert not list(c.carpeta.iterdir())


def test_aceptar_crea_una_vez_y_bloquea_replay(c):
    inicial = c.llamar('registrar_reclamo', ARGS)
    r = continuar(c, inicial)
    assert r['result']['structuredContent']['creado'] is True
    assert len(list(c.carpeta.iterdir())) == 1
    assert continuar(c, inicial)['result']['isError'] is True
    assert len(list(c.carpeta.iterdir())) == 1


@pytest.mark.parametrize('action,confirmar', [('decline', True), ('cancel', True), ('accept', False)])
def test_rechazo_no_escribe(c, action, confirmar):
    r = continuar(c, c.llamar('registrar_reclamo', ARGS), action, confirmar)
    assert 'cancelado' in r['result']['content'][0]['text']
    assert not list(c.carpeta.iterdir())


def test_contenido_alterado_no_escribe(c):
    r = continuar(c, c.llamar('registrar_reclamo', ARGS), args={**ARGS, 'descripcion': 'Otro reclamo alterado por un atacante'})
    # El SDK autentica requestState y lo liga a los argumentos antes del handler.
    assert r['error']['code'] == -32602
    assert r['error']['data']['reason'] == 'invalid_request_state'
    assert not list(c.carpeta.iterdir())


def test_token_inventado_no_escribe(c):
    r = continuar(c, {'result': {'requestState': 'inventado'}})
    assert r['error']['code'] == -32602
    assert r['error']['data']['reason'] == 'invalid_request_state'
    assert not list(c.carpeta.iterdir())
