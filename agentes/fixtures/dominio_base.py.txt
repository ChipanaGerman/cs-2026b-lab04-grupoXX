"""
PicanteríaYa — Módulo Pedidos: dominio.py
Esqueleto generado con apoyo de IA (Claude) a partir de docs/design/clases.puml
y revisado manualmente para coherencia con el ADR-001 (monolito modular +
puertos y adaptadores).

Generado: 2026-10-07
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from uuid import UUID


# ─────────────────────────────────────────────────────────────────────────────
# Enumeraciones
# ─────────────────────────────────────────────────────────────────────────────

class EstadoPedido(Enum):
    RECIBIDO = "RECIBIDO"
    PAGADO = "PAGADO"
    PREPARANDO = "PREPARANDO"
    EN_CAMINO = "EN_CAMINO"
    ENTREGADO = "ENTREGADO"
    CANCELADO = "CANCELADO"


class MedioPago(Enum):
    YAPE = "YAPE"


# ─────────────────────────────────────────────────────────────────────────────
# Entidades del dominio
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Cliente:
    nombre: str
    telefono: str
    distrito: str
    id: UUID = field(default_factory=uuid.uuid4)

    def realizar_pedido(self, picanteria: "Picanteria") -> "Pedido":
        """Crea un nuevo pedido vacío asociado a este cliente y picantería."""
        return Pedido(cliente=self, picanteria=picanteria)


@dataclass
class Picanteria:
    nombre: str
    direccion: str
    distrito: str
    telefono: str
    id: UUID = field(default_factory=uuid.uuid4)
    menus: List["Menu"] = field(default_factory=list)

    def publicar_menu(self, menu: "Menu") -> None:
        """Agrega un menú del día a la picantería."""
        self.menus.append(menu)


@dataclass
class Plato:
    nombre: str
    descripcion: str
    precio_unitario: Decimal
    stock_disponible: int
    id: UUID = field(default_factory=uuid.uuid4)

    def hay_stock(self, cantidad: int) -> bool:
        return self.stock_disponible >= cantidad

    def reservar(self, cantidad: int) -> None:
        if not self.hay_stock(cantidad):
            raise ValueError(f"Stock insuficiente para '{self.nombre}'")
        self.stock_disponible -= cantidad

    def liberar(self, cantidad: int) -> None:
        self.stock_disponible += cantidad


@dataclass
class Menu:
    fecha: datetime
    activo: bool = True
    platos: List[Plato] = field(default_factory=list)
    id: UUID = field(default_factory=uuid.uuid4)

    def activar(self) -> None:
        self.activo = True

    def desactivar(self) -> None:
        self.activo = False

    def obtener_platos_disponibles(self) -> List[Plato]:
        return [p for p in self.platos if p.stock_disponible > 0]


@dataclass
class LineaPedido:
    plato: Plato
    cantidad: int
    precio_unitario: Decimal

    def subtotal(self) -> Decimal:
        return self.precio_unitario * self.cantidad


@dataclass
class Pago:
    monto: Decimal
    medio: MedioPago
    codigo_operacion: str
    aprobado: bool
    fecha_hora: datetime = field(default_factory=datetime.now)
    id: UUID = field(default_factory=uuid.uuid4)


@dataclass
class Pedido:
    cliente: Cliente
    picanteria: Picanteria
    estado: EstadoPedido = EstadoPedido.RECIBIDO
    lineas: List[LineaPedido] = field(default_factory=list)
    pago: Optional[Pago] = None
    total_calculado: Decimal = Decimal("0.00")
    fecha: datetime = field(default_factory=datetime.now)
    id: UUID = field(default_factory=uuid.uuid4)

    def agregar_linea(self, plato: Plato, cantidad: int) -> None:
        """Agrega una línea al pedido, verificando stock."""
        if not plato.hay_stock(cantidad):
            raise ValueError(f"Stock insuficiente para '{plato.nombre}'")
        linea = LineaPedido(
            plato=plato,
            cantidad=cantidad,
            precio_unitario=plato.precio_unitario,
        )
        self.lineas.append(linea)

    def calcular_total(self) -> Decimal:
        """Calcula y almacena el total del pedido."""
        self.total_calculado = sum(l.subtotal() for l in self.lineas)
        return self.total_calculado

    def confirmar(self) -> None:
        """Reserva el stock de cada línea y marca el pedido como confirmado
        (en espera de pago)."""
        if not self.lineas:
            raise ValueError("El pedido no tiene líneas.")
        for linea in self.lineas:
            linea.plato.reservar(linea.cantidad)

    def registrar_pago(self, pago: Pago) -> None:
        """Asocia el pago al pedido y actualiza el estado a PAGADO."""
        self.pago = pago
        if pago.aprobado:
            self.estado = EstadoPedido.PAGADO
        else:
            self.cancelar("pago rechazado")

    def cancelar(self, motivo: str) -> None:
        """Cancela el pedido y libera el stock reservado."""
        self.estado = EstadoPedido.CANCELADO
        for linea in self.lineas:
            linea.plato.liberar(linea.cantidad)

    def marcar_preparando(self) -> None:
        self.estado = EstadoPedido.PREPARANDO

    def marcar_en_camino(self) -> None:
        self.estado = EstadoPedido.EN_CAMINO

    def confirmar_entrega(self) -> None:
        self.estado = EstadoPedido.ENTREGADO


@dataclass
class Repartidor:
    nombre: str
    telefono: str
    latitud: float
    longitud: float
    disponible: bool = True
    id: UUID = field(default_factory=uuid.uuid4)

    def actualizar_posicion(self, lat: float, lon: float) -> None:
        self.latitud = lat
        self.longitud = lon

    def asignar_pedido(self, pedido: Pedido) -> None:
        """Asigna este repartidor al pedido y lo marca como no disponible."""
        self.disponible = False
        pedido.marcar_preparando()


# ─────────────────────────────────────────────────────────────────────────────
# Puertos (interfaces — ADR-001: puertos y adaptadores)
# ─────────────────────────────────────────────────────────────────────────────

class PasarelaPago(ABC):
    """Puerto hacia el proveedor de pagos intermediario (Culqi/Niubiz)."""

    @abstractmethod
    def cobrar(self, monto: Decimal, telefono: str, referencia: str) -> Pago:
        """Procesa el cobro y retorna un objeto Pago con el resultado."""
        ...


class RepositorioPedidos(ABC):
    """Puerto hacia la capa de persistencia."""

    @abstractmethod
    def buscar(self, pedido_id: UUID) -> Pedido:
        ...

    @abstractmethod
    def guardar(self, pedido: Pedido) -> None:
        ...


class ColaMensajes(ABC):
    """Puerto hacia la cola de mensajes asíncrona (Redis/Celery)."""

    @abstractmethod
    def encolar_asignacion_repartidor(self, pedido_id: UUID) -> None:
        ...


class Notificador(ABC):
    """Puerto hacia el servicio de notificaciones (push/SMS/WhatsApp)."""

    @abstractmethod
    def notificar_confirmacion(self, pedido: Pedido) -> None:
        ...

    @abstractmethod
    def notificar_cancelacion(self, pedido: Pedido, motivo: str) -> None:
        ...


# ─────────────────────────────────────────────────────────────────────────────
# Adaptadores (stubs — integración real pendiente)
# ─────────────────────────────────────────────────────────────────────────────

class CulqiYapeAdapter(PasarelaPago):
    """Adaptador para cobros con Yape vía Culqi."""

    def cobrar(self, monto: Decimal, telefono: str, referencia: str) -> Pago:
        raise NotImplementedError("Integrar con la API de Culqi para Yape")


class CeleryColaMensajesAdapter(ColaMensajes):
    """Adaptador para la cola Redis/Celery."""

    def encolar_asignacion_repartidor(self, pedido_id: UUID) -> None:
        raise NotImplementedError("Integrar con Celery: task asignar_repartidor")


# ─────────────────────────────────────────────────────────────────────────────
# Servicio de aplicación
# ─────────────────────────────────────────────────────────────────────────────

class ServicioPedidos:
    """Orquesta el flujo 'pedir el menú del día y pagar con Yape'."""

    def __init__(
        self,
        repositorio: RepositorioPedidos,
        pasarela: PasarelaPago,
        cola: ColaMensajes,
        notificador: Notificador,
    ) -> None:
        self._repositorio = repositorio
        self._pasarela = pasarela
        self._cola = cola
        self._notificador = notificador

    def pedir_y_pagar(
        self,
        cliente: Cliente,
        picanteria: Picanteria,
        lineas: list[tuple[Plato, int]],
        medio: MedioPago,
    ) -> Pedido:
        """
        Crea el pedido, verifica stock, cobra con Yape y encola la asignación
        del repartidor de forma asíncrona.
        """
        pedido = Pedido(cliente=cliente, picanteria=picanteria)

        for plato, cantidad in lineas:
            pedido.agregar_linea(plato, cantidad)

        total = pedido.calcular_total()
        pedido.confirmar()

        pago = self._pasarela.cobrar(total, cliente.telefono, str(pedido.id))
        pedido.registrar_pago(pago)
        self._repositorio.guardar(pedido)

        if pago.aprobado:
            self._cola.encolar_asignacion_repartidor(pedido.id)
            self._notificador.notificar_confirmacion(pedido)
        else:
            self._notificador.notificar_cancelacion(pedido, "pago rechazado")

        return pedido

    def cancelar_pedido(self, pedido_id: UUID, motivo: str) -> Pedido:
        pedido = self._repositorio.buscar(pedido_id)
        pedido.cancelar(motivo)
        self._repositorio.guardar(pedido)
        self._notificador.notificar_cancelacion(pedido, motivo)
        return pedido
