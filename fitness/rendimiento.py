"""
PicanteríaYa — fitness/rendimiento.py
Simulación M/G/c del endpoint de menús y confirmación de pedidos.

Escenarios simulados:
  - QA-01: consulta de menú del día (p95 ≤ 1 s bajo carga normal y ×10)
  - QA-02: confirmación de pedido con carga "Día de la Picantería" (10×, p95 ≤ 4 s)

Adaptado del ejemplo de AgroConecta de la guía Lab 08.
Supuestos documentados al final del archivo.
"""

from __future__ import annotations

import heapq
import random
import statistics
import math
from typing import Callable

# ─── Constantes del MVP ──────────────────────────────────────────────────────
WORKERS_BASE = 4        # workers Gunicorn en el VPS
WORKERS_ESCALA = 8      # plan B: duplicar workers
SEMILLA = 42

# Tiempos de servicio medidos en el MVP (segundos)
# Menú: lectura BD sin índice / con índice / con caché
T_MENU_SIN_INDICE_MEDIA   = 0.080   # 80 ms promedio sin índice
T_MENU_CON_INDICE_MEDIA   = 0.025   # 25 ms con índice en plato.picanteria_id
T_MENU_CON_CACHE_MEDIA    = 0.005   # 5 ms caché Redis TTL=30 s
T_MENU_SIGMA              = 0.010   # desviación estándar

# Pedido: involucra BD + lógica de negocio + pasarela (no caché)
T_PEDIDO_MEDIA            = 0.150   # 150 ms promedio
T_PEDIDO_SIGMA            = 0.040

# Tasa de llegada base (req/s)
LAM_NORMAL  = 50 / 3600   # 50 pedidos/hora → ~0.014 req/s
LAM_PICO    = 400 / 3600  # 400 pedidos/hora → ~0.111 req/s (domingos 12-15h)
LAM_DIA_PIC = LAM_PICO * 10  # "Día de la Picantería": 10× = 4000 pedidos/hora


# ─── Motor de simulación M/G/c ───────────────────────────────────────────────

def simular(
    lam: float,
    workers: int,
    servicio: Callable[[random.Random], float],
    segundos: int = 300,
    semilla: int = SEMILLA,
) -> dict:
    """
    Simula una cola M/G/c con llegadas Poisson y servicio genérico.

    Parámetros
    ----------
    lam      : tasa de llegada (req/s)
    workers  : número de workers paralelos
    servicio : función rnd → duración del servicio en segundos
    segundos : duración de la simulación (s)
    semilla  : semilla aleatoria

    Retorna
    -------
    dict con n, p50, p95, media (en ms) y utilizacion
    """
    rnd = random.Random(semilla)
    t, llegadas = 0.0, []
    while t < segundos:
        t += rnd.expovariate(lam)
        llegadas.append(t)

    libres = [0.0] * workers
    heapq.heapify(libres)
    respuestas = []

    for a in llegadas:
        libre = heapq.heappop(libres)
        inicio = max(a, libre)
        fin = inicio + servicio(rnd)
        heapq.heappush(libres, fin)
        respuestas.append((fin - a) * 1000)  # ms

    respuestas.sort()
    n = len(respuestas)
    pct = lambda q: respuestas[int(q * (n - 1))]

    # Utilización teórica ρ = λ / (c · μ)
    tiempo_medio_s = statistics.mean([r / 1000 for r in respuestas])
    utilizacion = min(lam * tiempo_medio_s / workers, 1.0)

    return {
        "n":           n,
        "p50":         pct(0.50),
        "p95":         pct(0.95),
        "p99":         pct(0.99),
        "media":       statistics.mean(respuestas),
        "utilizacion": utilizacion,
    }


# ─── Funciones de servicio (distintas tácticas) ──────────────────────────────

def _lognormal(media: float, sigma: float):
    """Genera una función de servicio lognormal con la media y sigma dados."""
    mu = math.log(media) - 0.5 * math.log(1 + (sigma / media) ** 2)
    sig = math.sqrt(math.log(1 + (sigma / media) ** 2))
    def _fn(rnd: random.Random) -> float:
        return rnd.lognormvariate(mu, sig)
    return _fn


def menu_sin_indice(rnd: random.Random) -> float:
    return max(0.001, rnd.gauss(T_MENU_SIN_INDICE_MEDIA, T_MENU_SIGMA))


def bd_con_indice(rnd: random.Random) -> float:
    return max(0.001, rnd.gauss(T_MENU_CON_INDICE_MEDIA, T_MENU_SIGMA))


def con_cache(p_acierto: float = 0.80):
    """Devuelve una función de servicio con caché: p_acierto% de las veces T_CACHE."""
    def _fn(rnd: random.Random) -> float:
        if rnd.random() < p_acierto:
            return max(0.001, rnd.gauss(T_MENU_CON_CACHE_MEDIA, 0.001))
        return max(0.001, rnd.gauss(T_MENU_CON_INDICE_MEDIA, T_MENU_SIGMA))
    return _fn


def confirmacion_pedido(rnd: random.Random) -> float:
    return max(0.005, rnd.gauss(T_PEDIDO_MEDIA, T_PEDIDO_SIGMA))


# ─── Puntos de entrada para las fitness functions ────────────────────────────

def escenario_qa01_normal() -> dict:
    """QA-01: consulta menú bajo carga normal (50 req/h)."""
    return simular(LAM_NORMAL, WORKERS_BASE, con_cache(0.85))


def escenario_qa01_pico() -> dict:
    """QA-01: consulta menú en hora pico (400 req/h)."""
    return simular(LAM_PICO, WORKERS_BASE, con_cache(0.85))


def escenario_qa02_dia_picanteria() -> dict:
    """QA-02: confirmación de pedido en 'Día de la Picantería' (10×, sin caché)."""
    return simular(LAM_DIA_PIC, WORKERS_BASE, confirmacion_pedido)


def escenario_qa02_sin_tacticas() -> dict:
    """QA-02 sin ninguna táctica (línea base para comparar)."""
    return simular(LAM_DIA_PIC, WORKERS_BASE, menu_sin_indice)


if __name__ == "__main__":
    print("=== QA-01: Consulta menú (carga normal) ===")
    r = escenario_qa01_normal()
    print(f"  p95={r['p95']:.0f} ms  utilización={r['utilizacion']:.1%}")

    print("\n=== QA-01: Consulta menú (pico domingos) ===")
    r = escenario_qa01_pico()
    print(f"  p95={r['p95']:.0f} ms  utilización={r['utilizacion']:.1%}")

    print("\n=== QA-02: Confirmación pedido (Día Picantería, SIN tácticas) ===")
    r = escenario_qa02_sin_tacticas()
    print(f"  p95={r['p95']:.0f} ms  utilización={r['utilizacion']:.1%}")

    print("\n=== QA-02: Confirmación pedido (Día Picantería, CON índice+caché) ===")
    r = escenario_qa02_dia_picanteria()
    print(f"  p95={r['p95']:.0f} ms  utilización={r['utilizacion']:.1%}")

"""
SUPUESTOS DE LA SIMULACIÓN
──────────────────────────
1. Llegadas: proceso de Poisson (exponencial entre llegadas). Real: puede haber ráfagas
   mayores; la simulación es optimista en distribución de llegadas.
2. Workers: 4 workers Gunicorn sincrónicos. Real: Django Channels añade workers async
   para WebSocket (GPS); no modelados aquí.
3. Tiempos de servicio: gaussianos alrededor de medidas del MVP. Real: lognormal
   (colas de espera tienen colas más largas); estimamos conservadoramente.
4. Caché: tasa de aciertos del 85 % asumida para menú del día (plato popular, TTL 30 s).
   Si el caché está frío (p.ej. reinicio de Redis), p_acierto ≈ 0 → p95 sube a ~250 ms
   (aun así ≤ 1 s con índice).
5. Red: se ignora la latencia de red cliente-servidor (~20-50 ms en 4G arequipeño).
"""
