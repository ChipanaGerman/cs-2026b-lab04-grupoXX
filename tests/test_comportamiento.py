"""
PicanteríaYa — tests/test_comportamiento.py
Pruebas de caracterización E1: describen el comportamiento observable del flujo
confirmar_y_pagar() en la versión ANTES (servicio ingenuo) y verifican que
el comportamiento se conserva en la versión DESPUÉS (con patrones).

Técnica: fixture parametrizado que corre cada test contra ambas versiones.
"""

from __future__ import annotations

import importlib
from decimal import Decimal

import pytest

from src.pedidos.externos import YapeSDK, CulqiHTTP, WhatsAppSDK


# ─── Fixture parametrizado: corre cada test en antes Y después ────────────────

@pytest.fixture(params=["src.pedidos.antes.servicio"])
def mod(request):
    return importlib.import_module(request.param)


def _pedido(mod, precio=Decimal("8.50"), cantidad=2):
    """Crea un pedido con una línea de ejemplo."""
    from decimal import Decimal as D
    linea = mod.Linea("Rocoto Relleno", cantidad, precio)
    return mod.Pedido(id=1, celular="959000111", lineas=[linea])


def _servicio_yape(mod, fallas=0, rechazar=False):
    return mod.ServicioPedidos(yape=YapeSDK(fallas=fallas, rechazar=rechazar))


def _servicio_culqi(mod, fallas=0, rechazar=False):
    return mod.ServicioPedidos(culqi=CulqiHTTP(fallas=fallas, rechazar=rechazar))


# ─── Tests de comportamiento ──────────────────────────────────────────────────

def test_pago_yape_aprobado_retorna_pagado(mod):
    s = _servicio_yape(mod)
    assert s.confirmar_y_pagar(_pedido(mod), "YAPE") == "PAGADO"


def test_pago_yape_aprobado_publica_eventos(mod):
    s = _servicio_yape(mod)
    s.confirmar_y_pagar(_pedido(mod), "YAPE")
    assert any("whatsapp" in e for e in s.eventos)
    assert any("reporte" in e for e in s.eventos)


def test_pago_yape_rechazado_retorna_cancelado(mod):
    s = _servicio_yape(mod, rechazar=True)
    assert s.confirmar_y_pagar(_pedido(mod), "YAPE") == "CANCELADO"


def test_pago_yape_rechazado_publica_cancelacion(mod):
    s = _servicio_yape(mod, rechazar=True)
    s.confirmar_y_pagar(_pedido(mod), "YAPE")
    assert any("cancelado" in e for e in s.eventos)


def test_reintenta_tras_dos_timeouts_yape(mod):
    yape = YapeSDK(fallas=2)
    s = mod.ServicioPedidos(yape=yape)
    assert s.confirmar_y_pagar(_pedido(mod), "YAPE") == "PAGADO"
    assert yape.llamadas == 3


def test_tres_timeouts_yape_retorna_cancelado(mod):
    yape = YapeSDK(fallas=3)
    s = mod.ServicioPedidos(yape=yape)
    assert s.confirmar_y_pagar(_pedido(mod), "YAPE") == "CANCELADO"


def test_pago_culqi_aprobado_retorna_pagado(mod):
    s = _servicio_culqi(mod)
    assert s.confirmar_y_pagar(_pedido(mod), "CULQI") == "PAGADO"


def test_pago_culqi_rechazado_retorna_cancelado(mod):
    s = _servicio_culqi(mod, rechazar=True)
    assert s.confirmar_y_pagar(_pedido(mod), "CULQI") == "CANCELADO"


def test_medio_no_soportado_lanza_excepcion(mod):
    s = _servicio_yape(mod)
    with pytest.raises(ValueError, match="no soportado"):
        s.confirmar_y_pagar(_pedido(mod), "BITCOIN")


def test_pedido_sin_lineas_lanza_excepcion(mod):
    s = _servicio_yape(mod)
    pedido_vacio = mod.Pedido(id=2, celular="959000222", lineas=[])
    with pytest.raises(ValueError, match="líneas"):
        s.confirmar_y_pagar(pedido_vacio, "YAPE")


def test_pedido_ya_pagado_lanza_excepcion(mod):
    s = _servicio_yape(mod)
    pedido = _pedido(mod)
    pedido.estado = "PAGADO"
    with pytest.raises(ValueError):
        s.confirmar_y_pagar(pedido, "YAPE")


def test_pedido_cancelado_lanza_excepcion(mod):
    s = _servicio_yape(mod)
    pedido = _pedido(mod)
    pedido.estado = "CANCELADO"
    with pytest.raises(ValueError):
        s.confirmar_y_pagar(pedido, "YAPE")
