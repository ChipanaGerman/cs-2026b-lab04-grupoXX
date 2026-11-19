import pytest
from tests.test_issue_01 import pedido_base
from src.pedidos.dominio import Repartidor, EstadoPedido


def test_issue_03_ocupado_no_muta_pedido():
    pedido = pedido_base()
    repartidor = Repartidor('Repartidor ficticio', '000000000', -16.4, -71.5, False)
    with pytest.raises(ValueError, match='ocupado'):
        repartidor.asignar_pedido(pedido)
    assert pedido.estado is EstadoPedido.RECIBIDO
    assert repartidor.disponible is False


def test_issue_03_disponible_se_ocupa_y_no_admite_segundo_pedido():
    primero, segundo = pedido_base(), pedido_base()
    repartidor = Repartidor('Repartidor ficticio', '000000000', -16.4, -71.5)
    repartidor.asignar_pedido(primero)
    assert primero.estado is EstadoPedido.PREPARANDO
    assert repartidor.disponible is False
    with pytest.raises(ValueError):
        repartidor.asignar_pedido(segundo)
    assert segundo.estado is EstadoPedido.RECIBIDO
