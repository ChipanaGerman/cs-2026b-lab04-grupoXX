"""
PicanteríaYa — externos.py
Servicios externos simulados con interfaces DISTINTAS entre sí (como en la realidad).
  - YapeSDK: cobra en soles, responde con diccionario {"ok": bool, "operacion": str}
  - CulqiHTTP: cobra en céntimos (int), responde con tupla (codigo_http, tx_id)
  - MapasGoogleSDK: devuelve distancia en metros como float
  - WhatsAppSDK: bandeja de mensajes enviados
"""

from __future__ import annotations
import random
import time


class YapeSDK:
    """SDK simulado de Yape. Cobra en soles y responde con dict."""

    def __init__(self, fallas: int = 0, rechazar: bool = False):
        self._fallas_restantes = fallas
        self._rechazar = rechazar
        self.llamadas = 0

    def realizar_cobro(self, celular: str, monto_soles: float) -> dict:
        self.llamadas += 1
        if self._fallas_restantes > 0:
            self._fallas_restantes -= 1
            raise TimeoutError("Timeout de red con Yape")
        if self._rechazar:
            return {"ok": False, "operacion": None}
        return {"ok": True, "operacion": f"YP-{random.randint(10000, 99999)}"}


class CulqiHTTP:
    """Cliente HTTP simulado de Culqi. Cobra en céntimos y devuelve tupla (HTTP, tx)."""

    def __init__(self, fallas: int = 0, rechazar: bool = False):
        self._fallas_restantes = fallas
        self._rechazar = rechazar
        self.llamadas = 0

    def charge(self, monto_centimos: int, celular: str) -> tuple[int, str]:
        self.llamadas += 1
        if self._fallas_restantes > 0:
            self._fallas_restantes -= 1
            raise TimeoutError("Timeout de red con Culqi")
        if self._rechazar:
            return (402, None)
        return (200, f"CQ-{random.randint(10000, 99999)}")


class MapasGoogleSDK:
    """SDK simulado de Google Maps. Devuelve distancia en metros."""

    def distance_meters(self, origen_lat: float, origen_lon: float,
                        destino_lat: float, destino_lon: float) -> float:
        # Simulado: distancia euclidiana * 111000 (aprox metros por grado)
        return ((destino_lat - origen_lat)**2 + (destino_lon - origen_lon)**2)**0.5 * 111000


class WhatsAppSDK:
    """SDK simulado de WhatsApp Business API. Acumula mensajes enviados."""

    def __init__(self):
        self.bandeja: list[str] = []

    def send_message(self, phone: str, template: str, params: dict) -> str:
        msg = f"[WA] {phone}: {template.format(**params)}"
        self.bandeja.append(msg)
        return f"wa-msg-{len(self.bandeja)}"
