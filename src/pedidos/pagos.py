"""
PicanteríaYa — pagos.py
Refactor E2: Strategy + Adapter + Factory + Decorator para los medios de pago.

Olores eliminados:
  - OLOR 1: if/elif por medio de pago → Strategy + Factory (el servicio ya no elige)
  - OLOR 2: conocer detalles de cada SDK → Adapter (traduce a la interfaz común)
  - OLOR 3: reintentos duplicados → Decorator ConReintentos
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# Resultado de un cobro (Value Object)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ResultadoPago:
    aprobado: bool
    operacion: Optional[str] = None


# ─────────────────────────────────────────────────────────────────────────────
# <<Strategy>> PasarelaPago — interfaz común (puerto)
# ─────────────────────────────────────────────────────────────────────────────

class PasarelaPago(ABC):
    """Puerto común. Todas las estrategias de pago se usan de la misma forma."""

    @abstractmethod
    def cobrar(self, monto: Decimal, celular: str) -> ResultadoPago:
        """Procesa el cobro y retorna un ResultadoPago."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# <<Adapter>> — traduce cada SDK externo a la interfaz PasarelaPago
# ─────────────────────────────────────────────────────────────────────────────

class YapeAdapter(PasarelaPago):
    """<<Adapter>> Traduce YapeSDK (dict, soles) → PasarelaPago."""

    def __init__(self, sdk):
        self._sdk = sdk

    def cobrar(self, monto: Decimal, celular: str) -> ResultadoPago:
        r = self._sdk.realizar_cobro(celular, float(monto))
        return ResultadoPago(r["ok"], r.get("operacion"))


class CulqiAdapter(PasarelaPago):
    """<<Adapter>> Traduce CulqiHTTP (tupla, céntimos) → PasarelaPago."""

    def __init__(self, cliente):
        self._cliente = cliente

    def cobrar(self, monto: Decimal, celular: str) -> ResultadoPago:
        codigo, tx = self._cliente.charge(int(round(float(monto) * 100)), celular)
        return ResultadoPago(codigo == 200, tx)


# ─────────────────────────────────────────────────────────────────────────────
# <<Decorator>> — agrega comportamientos sin modificar los adaptadores
# ─────────────────────────────────────────────────────────────────────────────

class ConReintentos(PasarelaPago):
    """<<Decorator>> Reintenta solo ante TimeoutError (no ante rechazos de pago)."""

    def __init__(self, interna: PasarelaPago, intentos: int = 3):
        self._interna = interna
        self._intentos = intentos

    def cobrar(self, monto: Decimal, celular: str) -> ResultadoPago:
        ultimo_error: Optional[Exception] = None
        for _ in range(self._intentos):
            try:
                return self._interna.cobrar(monto, celular)
            except TimeoutError as e:
                ultimo_error = e
                continue
        # Solo retorna False después de agotar los reintentos por timeout
        return ResultadoPago(False)


class ConLog(PasarelaPago):
    """<<Decorator>> Registra cada intento de cobro (para auditoría)."""

    def __init__(self, interna: PasarelaPago, bitacora: list):
        self._interna = interna
        self._bitacora = bitacora

    def cobrar(self, monto: Decimal, celular: str) -> ResultadoPago:
        resultado = self._interna.cobrar(monto, celular)
        self._bitacora.append(
            f"cobro | monto={monto} | celular={celular} | "
            f"aprobado={resultado.aprobado} | op={resultado.operacion}"
        )
        return resultado


# ─────────────────────────────────────────────────────────────────────────────
# <<Factory Method (registro)>> — crea la estrategia adecuada por nombre
# ─────────────────────────────────────────────────────────────────────────────

class FabricaPasarelas:
    """
    <<Factory>> con registro: el servicio pide la pasarela por nombre ('YAPE', 'CULQI');
    la fábrica crea el adaptador correcto envuelto en ConReintentos.
    Agregar un medio nuevo NO requiere modificar el servicio (principio Open/Closed).
    """

    def __init__(self):
        self._creadores: dict = {}

    def registrar(self, medio: str, creador) -> None:
        self._creadores[medio] = creador

    def crear(self, medio: str) -> PasarelaPago:
        if medio not in self._creadores:
            raise ValueError(f"Medio de pago no soportado: {medio}")
        return ConReintentos(self._creadores[medio]())


def fabrica_default() -> FabricaPasarelas:
    """Fábrica pre-configurada con los SDK reales (o simulados)."""
    from src.pedidos.externos import YapeSDK, CulqiHTTP
    fabrica = FabricaPasarelas()
    fabrica.registrar("YAPE", lambda: YapeAdapter(YapeSDK()))
    fabrica.registrar("CULQI", lambda: CulqiAdapter(CulqiHTTP()))
    return fabrica
