"""
PicanteríaYa — estados.py
Refactor E3: patrón State para el ciclo de vida del Pedido.

Implementa directamente el diagrama estados-pedido.mmd del Lab 05:
  RECIBIDO → PAGADO → PREPARANDO → EN_CAMINO → ENTREGADO
  RECIBIDO → CANCELADO
  PAGADO → CANCELADO

Olor eliminado:
  - OLOR 4: condicionales anidados sobre pedido.estado → cada estado
    redefine solo las transiciones permitidas; una transición inválida
    es IMPOSIBLE por construcción (lanza ValueError en la clase base).
"""

from __future__ import annotations
from abc import ABC


# ─────────────────────────────────────────────────────────────────────────────
# <<State>> clase base — prohíbe todas las transiciones por defecto
# ─────────────────────────────────────────────────────────────────────────────

class EstadoPedido(ABC):
    """Clase base: cada transición lanza ValueError salvo que el estado la redefina."""

    nombre: str = "?"

    def registrar_pago(self, pedido) -> None:
        raise ValueError(f"No se puede registrar pago en estado {self.nombre}")

    def cancelar(self, pedido, motivo: str = "") -> None:
        raise ValueError(f"No se puede cancelar un pedido en estado {self.nombre}")

    def marcar_preparando(self, pedido) -> None:
        raise ValueError(f"No se puede preparar un pedido en estado {self.nombre}")

    def marcar_en_camino(self, pedido) -> None:
        raise ValueError(f"No se puede marcar en camino en estado {self.nombre}")

    def confirmar_entrega(self, pedido) -> None:
        raise ValueError(f"No se puede confirmar entrega en estado {self.nombre}")

    def __str__(self) -> str:
        return self.nombre


# ─────────────────────────────────────────────────────────────────────────────
# <<ConcreteState>> — un estado por cada nodo del diagrama de estados (Lab 05)
# ─────────────────────────────────────────────────────────────────────────────

class Recibido(EstadoPedido):
    """RECIBIDO: pedido creado, esperando confirmación de pago."""
    nombre = "RECIBIDO"

    def registrar_pago(self, pedido) -> None:
        """registrarPago() [pago aprobado] → PAGADO"""
        if pedido.pago and pedido.pago.aprobado:
            pedido._cambiar_estado(Pagado())
        else:
            # pago rechazado → CANCELADO
            pedido._cambiar_estado(Cancelado())

    def cancelar(self, pedido, motivo: str = "") -> None:
        """cancelar() [cliente cancela antes de pagar] → CANCELADO"""
        pedido._cambiar_estado(Cancelado())


class Pagado(EstadoPedido):
    """PAGADO: pago confirmado, encolando asignación de repartidor."""
    nombre = "PAGADO"

    def marcar_preparando(self, pedido) -> None:
        """marcarPreparando() [repartidor asignado] → PREPARANDO"""
        pedido._cambiar_estado(Preparando())

    def cancelar(self, pedido, motivo: str = "") -> None:
        """cancelar() [picantería sin capacidad] → CANCELADO"""
        pedido._cambiar_estado(Cancelado())


class Preparando(EstadoPedido):
    """PREPARANDO: el repartidor fue asignado, la picantería está preparando."""
    nombre = "PREPARANDO"

    def marcar_en_camino(self, pedido) -> None:
        """marcarEnCamino() [pedido listo para entrega] → EN_CAMINO"""
        pedido._cambiar_estado(EnCamino())


class EnCamino(EstadoPedido):
    """EN_CAMINO: el repartidor está llevando el pedido al cliente."""
    nombre = "EN_CAMINO"

    def confirmar_entrega(self, pedido) -> None:
        """confirmarEntrega() [cliente confirma recepción] → ENTREGADO"""
        pedido._cambiar_estado(Entregado())


class Entregado(EstadoPedido):
    """ENTREGADO: estado final exitoso."""
    nombre = "ENTREGADO"
    # No hay transiciones desde ENTREGADO


class Cancelado(EstadoPedido):
    """CANCELADO: estado final de cancelación."""
    nombre = "CANCELADO"
    # No hay transiciones desde CANCELADO


# ─────────────────────────────────────────────────────────────────────────────
# <<Context>> — la entidad Pedido delega al estado actual
# ─────────────────────────────────────────────────────────────────────────────

class Pedido:
    """
    Contexto del patrón State. Delega todas las transiciones al estado actual.
    El código cliente nunca manipula pedido.estado directamente.
    """

    def __init__(self, id: int, celular: str, lineas: list | None = None):
        self.id = id
        self.celular = celular
        self.lineas = lineas or []
        self.pago = None
        self._estado: EstadoPedido = Recibido()

    @property
    def estado(self) -> str:
        return self._estado.nombre

    def _cambiar_estado(self, nuevo: EstadoPedido) -> None:
        """Solo llamado desde los estados concretos."""
        self._estado = nuevo

    # ── delegación al estado actual ──────────────────────────────────────────

    def registrar_pago(self, pago) -> None:
        self.pago = pago
        self._estado.registrar_pago(self)

    def cancelar(self, motivo: str = "") -> None:
        self._estado.cancelar(self, motivo)

    def marcar_preparando(self) -> None:
        self._estado.marcar_preparando(self)

    def marcar_en_camino(self) -> None:
        self._estado.marcar_en_camino(self)

    def confirmar_entrega(self) -> None:
        self._estado.confirmar_entrega(self)

    def total(self):
        from decimal import Decimal
        return sum(l.cantidad * l.precio for l in self.lineas)
