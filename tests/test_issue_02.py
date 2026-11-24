from decimal import Decimal
import pytest
from tests.test_issue_01 import pedido_base
from src.pedidos.dominio import Plato


@pytest.mark.parametrize('cantidad', [0, -1, True, 1.5, '2', None])
def test_issue_02_rechaza_cantidad_invalida_sin_mutar(cantidad):
    pedido = pedido_base()
    plato = Plato('Adobo', '', Decimal('18.00'), 8)
    with pytest.raises(ValueError, match='entero positivo'):
        pedido.agregar_linea(plato, cantidad)
    assert pedido.lineas == []
    assert plato.stock_disponible == 8


def test_issue_02_acepta_entero_y_respeta_stock():
    pedido = pedido_base()
    plato = Plato('Adobo', '', Decimal('18.00'), 8)
    pedido.agregar_linea(plato, 2)
    assert pedido.calcular_total() == Decimal('36.00')
    with pytest.raises(ValueError, match='Stock insuficiente'):
        pedido.agregar_linea(plato, 9)
