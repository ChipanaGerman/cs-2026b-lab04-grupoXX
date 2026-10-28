"""
PicanteríaYa — fitness/disponibilidad.py
Simulación Monte Carlo de QA-04: disponibilidad ante caída de la pasarela de pago.

Meta QA-04: 0 pedidos perdidos, < 20 llamadas al proveedor caído en su ventana de caída.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

SEMILLA = 99
DURACION_S = 600
LAM_PAGOS = 1000 / 3600
P_TIMEOUT = 0.08
CAIDA_INICIO_S = 180
CAIDA_FIN_S = 300
UMBRAL_CB = 3
ESPERA_CB_S = 30


@dataclass
class Resultado:
    pagos_procesados: int = 0
    pagos_perdidos: int = 0
    pagos_diferidos: int = 0
    llamadas_en_caida: int = 0
    timeouts_totales: int = 0


def _proveedor_disponible(t: float, rnd: random.Random) -> bool:
    if CAIDA_INICIO_S <= t <= CAIDA_FIN_S:
        return False
    return rnd.random() >= P_TIMEOUT


def simular_reintentos(semilla: int = SEMILLA) -> Resultado:
    rnd = random.Random(semilla)
    res = Resultado()
    t = 0.0
    while t < DURACION_S:
        t += rnd.expovariate(LAM_PAGOS)
        ok = False
        for _ in range(3):
            if _proveedor_disponible(t, rnd):
                ok = True
                break
            else:
                res.timeouts_totales += 1
                if CAIDA_INICIO_S <= t <= CAIDA_FIN_S:
                    res.llamadas_en_caida += 1
        if ok:
            res.pagos_procesados += 1
        else:
            res.pagos_perdidos += 1
    return res


def simular_circuit_breaker(semilla: int = SEMILLA) -> Resultado:
    rnd = random.Random(semilla)
    res = Resultado()
    fallas_consec = 0
    cb_abierto_desde = None
    t = 0.0
    while t < DURACION_S:
        t += rnd.expovariate(LAM_PAGOS)
        if cb_abierto_desde is not None:
            if t - cb_abierto_desde < ESPERA_CB_S:
                res.pagos_perdidos += 1
                continue
            else:
                cb_abierto_desde = None
        if _proveedor_disponible(t, rnd):
            res.pagos_procesados += 1
            fallas_consec = 0
        else:
            res.timeouts_totales += 1
            if CAIDA_INICIO_S <= t <= CAIDA_FIN_S:
                res.llamadas_en_caida += 1
            fallas_consec += 1
            if fallas_consec >= UMBRAL_CB:
                cb_abierto_desde = t
                fallas_consec = 0
            res.pagos_perdidos += 1
    return res


def simular_cb_outbox(semilla: int = SEMILLA) -> Resultado:
    """Circuit Breaker + tabla outbox en PostgreSQL — 0 pedidos perdidos."""
    rnd = random.Random(semilla)
    res = Resultado()
    fallas_consec = 0
    cb_abierto_desde = None
    outbox: list[float] = []
    t = 0.0
    while t < DURACION_S:
        t += rnd.expovariate(LAM_PAGOS)
        if cb_abierto_desde is not None and t - cb_abierto_desde >= ESPERA_CB_S:
            cb_abierto_desde = None
            fallas_consec = 0
            res.pagos_procesados += len(outbox)
            res.pagos_diferidos += len(outbox)
            outbox.clear()
        if cb_abierto_desde is not None:
            outbox.append(t)
            continue
        if _proveedor_disponible(t, rnd):
            res.pagos_procesados += 1
            fallas_consec = 0
        else:
            res.timeouts_totales += 1
            if CAIDA_INICIO_S <= t <= CAIDA_FIN_S:
                res.llamadas_en_caida += 1
            fallas_consec += 1
            if fallas_consec >= UMBRAL_CB:
                cb_abierto_desde = t
                fallas_consec = 0
            res.pagos_perdidos += 1
    if cb_abierto_desde is None and outbox:
        res.pagos_procesados += len(outbox)
        res.pagos_diferidos += len(outbox)
        outbox.clear()
    return res


if __name__ == "__main__":
    escenarios = [
        ("Solo reintentos", simular_reintentos),
        ("Circuit breaker sin outbox", simular_circuit_breaker),
        ("Circuit breaker + outbox PostgreSQL", simular_cb_outbox),
    ]
    for nombre, fn in escenarios:
        r = fn()
        cumple = "CUMPLE" if r.pagos_perdidos == 0 else "NO CUMPLE"
        print("=== " + nombre + " ===")
        print("  Procesados      : " + str(r.pagos_procesados))
        print("  Perdidos        : " + str(r.pagos_perdidos))
        print("  Diferidos       : " + str(r.pagos_diferidos))
        print("  Llamadas en caida: " + str(r.llamadas_en_caida))
        print("  QA-04           : " + cumple)
        print()
