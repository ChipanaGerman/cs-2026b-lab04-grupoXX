"""
PicanteríaYa — antes/servicio.py
Versión INGENUA del flujo crítico "pedir menú y pagar con Yape/Culqi".

OLORES de código presentes (intencionales, para refactorizar en E2-E5):
  1. if/elif por medio de pago que creció cada vez que se agregó un método nuevo (L50-L80)
  2. El servicio conoce detalles internos de YapeSDK (dict) y CulqiHTTP (céntimos, tupla) (L54, L68)
  3. Bloque de reintentos duplicado para Yape y Culqi (L53-L60, L67-L74)
  4. Condicionales anidados sobre pedido["estado"] en lugar de delegar al objeto estado (L35-L48)
  5. El servicio notifica "a mano" a WhatsApp y arma el mensaje inline (L82-L88)
  6. sugerir_descripcion_plato() mezcla lógica de proveedores LLM con validaciones (L95-L125)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional

# Importamos los SDK simulados directamente (acoplamiento fuerte = olor)
from src.pedidos.externos import YapeSDK, CulqiHTTP, MapasGoogleSDK, WhatsAppSDK


@dataclass
class Linea:
    nombre_plato: str
    cantidad: int
    precio: Decimal


@dataclass
class Pedido:
    id: int
    celular: str
    lineas: List[Linea] = field(default_factory=list)
    estado: str = "RECIBIDO"
    operacion: Optional[str] = None

    def total(self) -> Decimal:
        return sum(l.cantidad * l.precio for l in self.lineas)


class ServicioPedidos:
    """Versión ingenua: todo en un solo método, sin patrones."""

    def __init__(self, yape=None, culqi=None, mapas=None, whatsapp=None):
        self.yape = yape or YapeSDK()
        self.culqi = culqi or CulqiHTTP()
        self.mapas = mapas or MapasGoogleSDK()
        self.whatsapp = whatsapp or WhatsAppSDK()
        self.eventos: List[str] = []

    def confirmar_y_pagar(self, pedido: Pedido, medio: str) -> str:
        # Validación del estado — condicionales anidados (OLOR 4)
        if pedido.estado != "RECIBIDO":
            if pedido.estado == "CANCELADO":
                raise ValueError("El pedido está cancelado")
            elif pedido.estado == "PAGADO":
                raise ValueError("El pedido ya fue pagado")
            else:
                raise ValueError(f"Estado no válido: {pedido.estado}")

        if not pedido.lineas:
            raise ValueError("El pedido no tiene líneas")

        total = pedido.total()
        pedido.estado = "CONFIRMADO"

        aprobado, operacion = False, None

        # if/elif por medio de pago — OLORES 1, 2 y 3
        if medio == "YAPE":
            for intento in range(3):
                try:
                    # Conoce detalles de YapeSDK (cobra en soles, dict) — OLOR 2
                    r = self.yape.realizar_cobro(pedido.celular, float(total))
                    aprobado, operacion = r["ok"], r.get("operacion")
                    break
                except TimeoutError:
                    if intento == 2:
                        aprobado = False

        elif medio == "CULQI":
            for intento in range(3):
                try:
                    # Conoce detalles de CulqiHTTP (cobra en céntimos, tupla) — OLOR 2
                    codigo, tx = self.culqi.charge(
                        int(round(float(total) * 100)), pedido.celular
                    )
                    aprobado, operacion = codigo == 200, tx
                    break
                except TimeoutError:
                    if intento == 2:
                        aprobado = False

        else:
            raise ValueError(f"Medio de pago no soportado: {medio}")

        if aprobado:
            pedido.estado = "PAGADO"
            pedido.operacion = operacion
            # Notifica "a mano" armando strings inline — OLOR 5
            self.eventos.append(
                f"whatsapp:{pedido.celular}:Pedido {pedido.id} confirmado y pagado"
            )
            self.eventos.append(f"reporte:{pedido.id}:{float(total):.2f}")
            self.whatsapp.send_message(
                pedido.celular,
                "Tu pedido {id} está confirmado. Total: S/ {total}",
                {"id": pedido.id, "total": f"{float(total):.2f}"},
            )
        else:
            pedido.estado = "CANCELADO"
            self.eventos.append(f"cancelado:{pedido.id}:pago_rechazado")

        return pedido.estado

    def asignar_repartidor(self, pedido: Pedido,
                           repartidores: list[dict]) -> Optional[dict]:
        """
        Asigna el repartidor más cercano disponible.
        Olor: si mañana queremos 'menos cargado' en vez de 'más cercano',
        hay que modificar este método (viola Open/Closed).
        """
        disponibles = [r for r in repartidores if r.get("disponible")]
        if not disponibles:
            return None

        lat_pic = pedido.__dict__.get("lat_picanteria", -16.39)
        lon_pic = pedido.__dict__.get("lon_picanteria", -71.53)

        mejor = min(
            disponibles,
            key=lambda r: self.mapas.distance_meters(
                r["lat"], r["lon"], lat_pic, lon_pic
            ),
        )
        return mejor

    def sugerir_descripcion_plato(self, nombre: str, proveedor: str = "GEMINI") -> str:
        """
        Genera una descripción de un plato usando IA.
        OLORES: if/elif por proveedor + validaciones mezcladas (OLOR 6).
        """
        prompt = (
            f"Escribe una descripción atractiva del plato '{nombre}' "
            "de la gastronomía arequipeña. Máximo 80 palabras. "
            "No incluyas precios ni afirmaciones de salud."
        )

        if proveedor == "GEMINI":
            # Simula llamada a Gemini API
            respuesta = f"[GEMINI] {nombre}: Delicioso plato tradicional arequipeño."
        elif proveedor == "OPENAI":
            respuesta = f"[OPENAI] {nombre}: Exquisita preparación de la cocina arequipeña."
        elif proveedor == "LOCAL":
            respuesta = f"[LOCAL] {nombre}: Sabor auténtico de Arequipa."
        else:
            raise ValueError(f"Proveedor LLM no soportado: {proveedor}")

        # Validaciones mezcladas con la lógica del proveedor — OLOR 6
        if "S/" in respuesta:
            raise ValueError("La IA incluyó un precio en la descripción")
        if "garantizado" in respuesta.lower():
            raise ValueError("La IA usó afirmación prohibida: 'garantizado'")
        if len(respuesta) > 500:
            respuesta = respuesta[:500]

        return respuesta
