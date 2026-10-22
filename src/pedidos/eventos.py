"""
PicanteríaYa — eventos.py
Refactor E4: Observer para notificaciones + Decorator de seguimiento GPS.

Olores eliminados:
  - OLOR 5: el servicio notificaba "a mano" a WhatsApp armando strings inline
    → Observer desacopla quién publica del quién recibe

Patrones implementados:
  - Observer: PublicadorEventos + Suscriptor (al menos 2 suscriptores)
  - Decorator: ConSeguimientoGPS envuelve un suscriptor para agregar log de posición
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, List


# ─────────────────────────────────────────────────────────────────────────────
# <<Observer>> interfaz Suscriptor
# ─────────────────────────────────────────────────────────────────────────────

class Suscriptor(ABC):
    """<<Observer>> Todo suscriptor recibe notificaciones vía actualizar()."""

    @abstractmethod
    def actualizar(self, evento: str, datos: dict) -> None: ...


# ─────────────────────────────────────────────────────────────────────────────
# <<Subject>> PublicadorEventos
# ─────────────────────────────────────────────────────────────────────────────

class PublicadorEventos:
    """
    <<Subject>> Mantiene la lista de suscriptores por tipo de evento
    y los notifica cuando se publica. Agregar un nuevo suscriptor NO requiere
    modificar el servicio (principio Open/Closed demostrado en test_patrones.py).
    """

    def __init__(self) -> None:
        self._suscriptores: Dict[str, List[Suscriptor]] = {}

    def suscribir(self, evento: str, suscriptor: Suscriptor) -> None:
        self._suscriptores.setdefault(evento, []).append(suscriptor)

    def desuscribir(self, evento: str, suscriptor: Suscriptor) -> None:
        if evento in self._suscriptores:
            self._suscriptores[evento].remove(suscriptor)

    def publicar(self, evento: str, datos: dict) -> None:
        for s in self._suscriptores.get(evento, []):
            s.actualizar(evento, datos)


# ─────────────────────────────────────────────────────────────────────────────
# <<ConcreteObserver>> Suscriptores concretos
# ─────────────────────────────────────────────────────────────────────────────

class NotificadorWhatsApp(Suscriptor):
    """<<ConcreteObserver>> Envía mensajes WhatsApp al cliente."""

    def __init__(self, sdk_whatsapp, bandeja_eventos: List[str]):
        self._sdk = sdk_whatsapp
        self._bandeja = bandeja_eventos

    def actualizar(self, evento: str, datos: dict) -> None:
        if evento == "pedido_pagado":
            self._sdk.send_message(
                datos["celular"],
                "Tu pedido {id} está confirmado. Total: S/ {total}",
                {"id": datos["id"], "total": f"{float(datos['total']):.2f}"},
            )
            self._bandeja.append(
                f"whatsapp:{datos['celular']}:Pedido {datos['id']} confirmado y pagado"
            )
        elif evento == "pedido_cancelado":
            self._sdk.send_message(
                datos["celular"],
                "Tu pedido {id} fue cancelado. Motivo: {motivo}",
                {"id": datos["id"], "motivo": datos.get("motivo", "")},
            )
            self._bandeja.append(
                f"whatsapp:{datos['celular']}:Pedido {datos['id']} cancelado"
            )


class RegistradorReportes(Suscriptor):
    """<<ConcreteObserver>> Registra el evento para reportes de ventas."""

    def __init__(self, bandeja_eventos: List[str]):
        self._bandeja = bandeja_eventos

    def actualizar(self, evento: str, datos: dict) -> None:
        if evento == "pedido_pagado":
            self._bandeja.append(
                f"reporte:{datos['id']}:{float(datos['total']):.2f}"
            )


class NotificadorPicanteria(Suscriptor):
    """<<ConcreteObserver>> Avisa a la picantería que debe preparar el pedido."""

    def __init__(self, bandeja_eventos: List[str]):
        self._bandeja = bandeja_eventos

    def actualizar(self, evento: str, datos: dict) -> None:
        if evento == "pedido_pagado":
            self._bandeja.append(
                f"picanteria:{datos.get('picanteria_id', '?')}:"
                f"preparar pedido {datos['id']}"
            )


# ─────────────────────────────────────────────────────────────────────────────
# <<Decorator>> sobre Suscriptor — agrega log de GPS sin modificar el suscriptor
# ─────────────────────────────────────────────────────────────────────────────

class ConSeguimientoGPS(Suscriptor):
    """
    <<Decorator>> Envuelve cualquier Suscriptor y agrega un log de posición GPS
    al momento de la notificación. Útil para el módulo Repartidores.
    """

    def __init__(self, interno: Suscriptor, log_gps: List[str]):
        self._interno = interno
        self._log_gps = log_gps

    def actualizar(self, evento: str, datos: dict) -> None:
        if "lat" in datos and "lon" in datos:
            self._log_gps.append(
                f"GPS | pedido={datos.get('id')} | "
                f"lat={datos['lat']} | lon={datos['lon']}"
            )
        self._interno.actualizar(evento, datos)
