"""
PicanteríaYa — servicio.py (versión DESPUÉS del refactor)
El método confirmar_y_pagar() pasó de complejidad 15 (C) a 3 (A).
"""

from __future__ import annotations
from decimal import Decimal
from typing import List

from src.pedidos.pagos import FabricaPasarelas
from src.pedidos.estados import Pedido
from src.pedidos.eventos import PublicadorEventos


class ServicioPedidos:
    """
    Orquesta el flujo 'pedir menú y pagar'. 
    Delega completamente a: FabricaPasarelas (Strategy+Factory),
    Pedido (State) y PublicadorEventos (Observer).
    """

    def __init__(self, fabrica: FabricaPasarelas, publicador: PublicadorEventos):
        self.fabrica = fabrica
        self.publicador = publicador

    def confirmar_y_pagar(self, pedido: Pedido, medio: str) -> str:
        pasarela = self.fabrica.crear(medio)          # Factory elige la Strategy
        resultado = pasarela.cobrar(pedido.total(), pedido.celular)

        if resultado.aprobado:
            from src.pedidos.estados import Pagado as PagoSimple
            class _Pago:
                aprobado = True
                operacion = resultado.operacion
            pedido.registrar_pago(_Pago())
            self.publicador.publicar("pedido_pagado", {
                "id": pedido.id,
                "celular": pedido.celular,
                "total": pedido.total(),
            })
        else:
            class _PagoRechazado:
                aprobado = False
                operacion = None
            pedido.registrar_pago(_PagoRechazado())
            self.publicador.publicar("pedido_cancelado", {
                "id": pedido.id,
                "celular": pedido.celular,
                "motivo": "pago rechazado",
            })

        return pedido.estado
