"""Contratos sobre el transporte real, sin LLM ni red."""
import pytest
from jsonschema import validate
from agentes.mcp.cliente.rpc import Cliente


@pytest.fixture(scope='module')
def cliente(tmp_path_factory):
    carpeta = tmp_path_factory.mktemp('reclamos')
    with Cliente(entorno={'PICANTERIA_RECLAMOS_DIR': str(carpeta)}) as c:
        c.carpeta = carpeta
        yield c


def test_descubrimiento_sin_initialize(cliente):
    r = cliente.pedir('server/discover')['result']
    assert '2026-07-28' in r['supportedVersions']
    assert r['resultType'] == 'complete'


def test_catalogo_estable(cliente):
    a = cliente.pedir('tools/list')['result']['tools']
    b = cliente.pedir('tools/list')['result']['tools']
    assert a == b
    assert [t['name'] for t in a] == ['menu_del_dia', 'pedidos_por_estado', 'registrar_reclamo']


def test_una_escritura(cliente):
    herramientas = cliente.pedir('tools/list')['result']['tools']
    assert [t['name'] for t in herramientas if not t['annotations']['readOnlyHint']] == ['registrar_reclamo']
    assert all(t['annotations']['destructiveHint'] is False for t in herramientas)


def test_menu_estructurado_y_schema(cliente):
    r = cliente.llamar('menu_del_dia', {'fecha': '2026-11-24', 'picanteria': 'La Tradición'})['result']
    t = cliente.pedir('tools/list')['result']['tools'][0]
    validate(r['structuredContent'], t['outputSchema'])
    assert len(r['structuredContent']['platos']) == 2
    assert r['structuredContent']['platos'][0]['precio_soles'] == '25.00'


@pytest.mark.parametrize('fecha', ['24/11/2026', '2026-02-30', '2026-11-23'])
def test_fecha_invalida(cliente, fecha):
    r = cliente.llamar('menu_del_dia', {'fecha': fecha, 'picanteria': 'La Tradición'})
    assert r['result']['isError'] is True
    assert r['result']['content'][0]['text']


def test_estado_invalido(cliente):
    r = cliente.llamar('pedidos_por_estado', {'estado': 'PENDIENTE'})['result']
    assert r['isError'] is True
    assert 'CANCELADO' in r['content'][0]['text']


def test_pedidos_sin_pii(cliente):
    r = cliente.llamar('pedidos_por_estado', {'estado': 'CANCELADO'})['result']['structuredContent']
    assert len(r['pedidos']) <= 20
    assert set(r['pedidos'][0]) == {'pedido_id', 'total_soles'}


def test_dos_recursos_y_plantilla(cliente):
    assert len(cliente.pedir('resources/list')['result']['resources']) >= 2
    assert cliente.pedir('resources/templates/list')['result']['resourceTemplates'][0]['uriTemplate'] == 'picanteria://adr/{numero}'
    assert 'Decisi' in cliente.pedir('resources/read', {'uri': 'picanteria://adr/001'})['result']['contents'][0]['text']


@pytest.mark.parametrize('ruta', ['../README.md', '%2e%2e%2fREADME.md', '000/../../README.md', 'abc'])
def test_recurso_rechaza_traversal(cliente, ruta):
    assert 'error' in cliente.pedir('resources/read', {'uri': 'picanteria://adr/'+ruta})


def test_prompt(cliente):
    assert cliente.pedir('prompts/list')['result']['prompts'][0]['name'] == 'responder_reclamo'
    r = cliente.pedir('prompts/get', {'name': 'responder_reclamo', 'arguments': {'descripcion': 'Pedido cancelado sin explicación'}})
    assert 'No inventes' in r['result']['messages'][0]['content']['text']


def test_uuid_invalido_no_escribe(cliente):
    r = cliente.llamar('registrar_reclamo', {'pedido_id': 'x'*36, 'descripcion': 'Pedido cancelado sin explicación'})
    assert r['result']['isError']
    assert not list(cliente.carpeta.iterdir())


def test_error_protocolo_distinto_de_negocio(cliente):
    r = cliente.pedir('metodo/inexistente')
    assert r['error']['code'] == -32601
    assert 'result' not in r
