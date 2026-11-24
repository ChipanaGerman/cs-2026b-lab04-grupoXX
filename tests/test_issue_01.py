from decimal import Decimal
from src.pedidos.dominio import Cliente, Picanteria, Pedido, Plato


def pedido_base():
    return Pedido(Cliente('Cliente ficticio', '000000000', 'Cayma'),
                  Picanteria('Picantería de prueba', 'Dirección ficticia', 'Cayma', '000000000'))


def test_issue_01_total_incluye_delivery_una_vez():
    pedido = pedido_base()
    pedido.costo_delivery = Decimal('5.50')
    pedido.agregar_linea(Plato('Rocoto', '', Decimal('20.00'), 10), 2)
    assert pedido.calcular_total() == Decimal('45.50')
    assert pedido.calcular_total() == Decimal('45.50')


def test_issue_01_pedido_vacio_conserva_decimal():
    assert isinstance(pedido_base().calcular_total(), Decimal)
