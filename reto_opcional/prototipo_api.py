"""
PicanteríaYa — reto_opcional/prototipo_api.py
Reto Opcional A: prototipo mínimo del endpoint crítico con FastAPI.

Simula el endpoint GET /menus/{picanteria_id} con:
  - Sin táctica: consulta directa (sleep que simula BD sin índice)
  - Con índice: consulta rápida (sleep que simula BD con índice)
  - Con caché: respuesta instantánea desde memoria

Ejecutar con:
    uvicorn reto_opcional.prototipo_api:app --reload --port 8000
Luego medir con:
    locust -f reto_opcional/locustfile.py --headless -u 50 -r 10 --run-time 30s --host http://localhost:8000
"""

from __future__ import annotations

import time
import random
import statistics
from typing import Annotated
from functools import lru_cache

try:
    from fastapi import FastAPI, Query
    from fastapi.responses import JSONResponse
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

# ─── Datos simulados ──────────────────────────────────────────────────────────
PICANTERIAS = {str(i): {"nombre": f"Picantería {i}", "platos": [
    {"id": j, "nombre": f"Plato {j}", "precio": 12.0 + j, "disponible": True}
    for j in range(1, 6)
]} for i in range(1, 11)}

# ─── Simulación de tiempos de BD ──────────────────────────────────────────────
T_BD_SIN_INDICE = 0.080   # 80 ms sin índice
T_BD_CON_INDICE = 0.025   # 25 ms con índice
T_BD_SIGMA      = 0.010   # desviación estándar

_cache: dict[str, dict] = {}   # caché en memoria (simula Redis)
CACHE_TTL_S = 30

def _bd_sin_indice(picanteria_id: str) -> dict:
    time.sleep(max(0, random.gauss(T_BD_SIN_INDICE, T_BD_SIGMA)))
    return PICANTERIAS.get(picanteria_id, {})

def _bd_con_indice(picanteria_id: str) -> dict:
    time.sleep(max(0, random.gauss(T_BD_CON_INDICE, T_BD_SIGMA)))
    return PICANTERIAS.get(picanteria_id, {})

def _con_cache(picanteria_id: str) -> dict:
    if picanteria_id in _cache:
        return _cache[picanteria_id]
    data = _bd_con_indice(picanteria_id)
    _cache[picanteria_id] = data
    return data


if FASTAPI_AVAILABLE:
    app = FastAPI(title="PicanteríaYa — Prototipo endpoint menú (Reto Opcional A)")

    @app.get("/menus/{picanteria_id}/sin-tacticas")
    async def menu_sin_tacticas(picanteria_id: str):
        """QA-01 sin tácticas: BD directa sin índice."""
        return _bd_sin_indice(picanteria_id)

    @app.get("/menus/{picanteria_id}/con-indice")
    async def menu_con_indice(picanteria_id: str):
        """QA-01 con índice: consulta BD optimizada."""
        return _bd_con_indice(picanteria_id)

    @app.get("/menus/{picanteria_id}/con-cache")
    async def menu_con_cache(picanteria_id: str):
        """QA-01 con caché: respuesta desde memoria (simula Redis)."""
        return _con_cache(picanteria_id)

    @app.get("/health")
    async def health():
        return {"status": "ok"}


# ─── Mini benchmark local (sin FastAPI) ───────────────────────────────────────
def benchmark_local(n: int = 200):
    """Ejecuta n requests simuladas para cada táctica y reporta p95."""
    print(f"\n=== Benchmark local (n={n} por táctica) ===")
    for nombre, fn in [
        ("Sin tacticas (sin indice)", _bd_sin_indice),
        ("Con indice", _bd_con_indice),
        ("Con cache (warm)", _con_cache),
    ]:
        # warmup
        _con_cache("1")
        tiempos = []
        for _ in range(n):
            t0 = time.perf_counter()
            fn(str(random.randint(1, 10)))
            tiempos.append((time.perf_counter() - t0) * 1000)
        tiempos.sort()
        p95 = tiempos[int(0.95 * len(tiempos))]
        media = statistics.mean(tiempos)
        print(f"  {nombre}: p95={p95:.1f} ms  media={media:.1f} ms  (umbral QA-01: 1000 ms)")


if __name__ == "__main__":
    benchmark_local(300)
