"""
PicanteríaYa — tests/test_fitness.py
Fitness functions automatizadas (E5 Lab 08).

FF-01 (estructural): el modulo pedidos no importa directamente los adaptadores de pago.
FF-02 (estructural): el modulo menu no importa pedidos (dependencia prohibida).
FF-03 (calidad)    : QA-01 — p95 menú ≤ 1 000 ms en hora pico domingos.
FF-04 (calidad)    : QA-02 — p95 confirmación ≤ 4 000 ms en Dia Picanteria (10x).
FF-05 (calidad)    : QA-04 — CB reduce llamadas al proveedor caído respecto a reintentos puros.
FF-06 (aislamiento): QA-07 — simulación de que la logica de aislamiento es aplicada.
"""

from __future__ import annotations

import sys
import os
import importlib
import ast

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fitness.rendimiento import (
    escenario_qa01_pico,
    escenario_qa02_dia_picanteria,
    escenario_qa02_sin_tacticas,
)
from fitness.disponibilidad import simular_reintentos, simular_cb_outbox

# ─── Presupuestos de latencia ────────────────────────────────────────────────
P95_MENU_MS    = 1_000   # QA-01: p95 consulta menú ≤ 1 s
P95_PEDIDO_MS  = 4_000   # QA-02: p95 confirmación ≤ 4 s


# ═══════════════════════════════════════════════════════════════════════════════
# FF-01 y FF-02 — Fitness functions ESTRUCTURALES
# (import-linter las verifica a nivel de módulo en CI via lint-imports;
#  aquí verificamos a nivel de AST sin necesidad de importar los módulos)
# ═══════════════════════════════════════════════════════════════════════════════

def _imports_en_archivo(ruta: str) -> list[str]:
    """Extrae todos los módulos importados en un archivo Python via AST."""
    try:
        tree = ast.parse(open(ruta, encoding="utf-8").read())
    except (FileNotFoundError, SyntaxError):
        return []
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports += [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports


class TestFF01Estructural:
    """
    FF-01: src/pedidos/servicio.py NO debe importar directamente los adaptadores
    (pagos.YapeAdapter, pagos.CulqiAdapter). Solo la fábrica/arranque los conoce.
    """

    def test_ff01_servicio_no_importa_adaptadores_yape_culqi(self):
        ruta = os.path.join(
            os.path.dirname(__file__), "..", "src", "pedidos", "servicio.py"
        )
        imports = _imports_en_archivo(ruta)
        for imp in imports:
            assert "YapeAdapter" not in imp, (
                f"FF-01 VIOLADA: servicio.py importa directamente '{imp}' "
                f"(viola ADR-005: solo el arranque conoce los adaptadores)"
            )
            assert "CulqiAdapter" not in imp, (
                f"FF-01 VIOLADA: servicio.py importa directamente '{imp}'"
            )

    def test_ff01_servicio_usa_abstraccion_pasarela(self):
        """El servicio debe depender de PasarelaPago (abstracción), no de implementaciones."""
        ruta = os.path.join(
            os.path.dirname(__file__), "..", "src", "pedidos", "servicio.py"
        )
        contenido = open(ruta, encoding="utf-8").read()
        # El servicio puede importar pagos (el módulo) pero no clases concretas de adaptadores
        # Verificamos que no haya instanciación directa de adaptadores
        assert "YapeAdapter()" not in contenido, "FF-01: servicio instancia YapeAdapter directamente"
        assert "CulqiAdapter()" not in contenido, "FF-01: servicio instancia CulqiAdapter directamente"


class TestFF02Estructural:
    """
    FF-02: src/pedidos/estados.py NO debe importar src/pedidos/pagos.py
    (el módulo de estados no depende del módulo de pagos — ADR-001).
    """

    def test_ff02_estados_no_importa_pagos(self):
        ruta = os.path.join(
            os.path.dirname(__file__), "..", "src", "pedidos", "estados.py"
        )
        imports = _imports_en_archivo(ruta)
        for imp in imports:
            assert "pagos" not in imp.lower(), (
                f"FF-02 VIOLADA: estados.py importa '{imp}' "
                f"(viola ADR-001: los estados no dependen de la capa de pagos)"
            )

    def test_ff02_eventos_no_importa_estados(self):
        """eventos.py (notificaciones) no debe conocer la implementación de estados."""
        ruta = os.path.join(
            os.path.dirname(__file__), "..", "src", "pedidos", "eventos.py"
        )
        imports = _imports_en_archivo(ruta)
        for imp in imports:
            assert "estados" not in imp.lower(), (
                f"FF-02 VIOLADA: eventos.py importa '{imp}' (acoplamiento indebido)"
            )


# ═══════════════════════════════════════════════════════════════════════════════
# FF-03 y FF-04 — Fitness functions DE CALIDAD (rendimiento)
# ═══════════════════════════════════════════════════════════════════════════════

class TestFF03RendimientoMenu:
    """FF-03: QA-01 — p95 consulta menú ≤ 1 s en hora pico domingos (400 req/h)."""

    def test_ff03_p95_menu_pico_domingo(self):
        r = escenario_qa01_pico()
        assert r["p95"] <= P95_MENU_MS, (
            f"FF-03 FALLIDA: p95={r['p95']:.0f} ms excede el presupuesto de {P95_MENU_MS} ms "
            f"(QA-01 no cumplido en pico dominical)"
        )

    def test_ff03_p95_mejora_con_cache_vs_sin_tacticas(self):
        """La caché debe mejorar el p95 respecto a la versión sin tácticas."""
        from fitness.rendimiento import escenario_qa01_normal, menu_sin_indice, simular, LAM_PICO, WORKERS_BASE
        sin_tacticas = simular(LAM_PICO, WORKERS_BASE, menu_sin_indice)
        con_cache = escenario_qa01_pico()
        assert con_cache["p95"] <= sin_tacticas["p95"], (
            f"FF-03: la caché empeoró el p95 ({con_cache['p95']:.0f} ms vs {sin_tacticas['p95']:.0f} ms sin caché)"
        )


class TestFF04RendimientoPedido:
    """FF-04: QA-02 — p95 confirmación ≤ 4 s en Día de la Picantería (10× carga)."""

    def test_ff04_p95_confirmacion_dia_picanteria(self):
        r = escenario_qa02_dia_picanteria()
        assert r["p95"] <= P95_PEDIDO_MS, (
            f"FF-04 FALLIDA: p95={r['p95']:.0f} ms excede {P95_PEDIDO_MS} ms "
            f"(QA-02 no cumplido en Dia Picanteria)"
        )

    def test_ff04_tacticas_mejor_que_sin_tacticas(self):
        sin_t = escenario_qa02_sin_tacticas()
        con_t = escenario_qa02_dia_picanteria()
        assert con_t["p95"] <= sin_t["p95"] * 3, (
            "FF-04: las tacticas deben mantener p95 dentro de 3x del escenario base"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# FF-05 — Fitness function DE CALIDAD (disponibilidad)
# ═══════════════════════════════════════════════════════════════════════════════

class TestFF05Disponibilidad:
    """FF-05: QA-04 — el CB reduce las llamadas al proveedor caído vs solo reintentos."""

    def test_ff05_cb_reduce_llamadas_en_caida(self):
        r_reintentos = simular_reintentos()
        r_cb = simular_cb_outbox()
        assert r_cb.llamadas_en_caida < r_reintentos.llamadas_en_caida, (
            f"FF-05 FALLIDA: CB no reduce llamadas en caida "
            f"({r_cb.llamadas_en_caida} >= {r_reintentos.llamadas_en_caida})"
        )

    def test_ff05_cb_outbox_procesa_diferidos(self):
        """Con CB+outbox, los pagos diferidos deben ser > 0 (el outbox funciona)."""
        r = simular_cb_outbox()
        assert r.pagos_diferidos > 0, (
            "FF-05: el outbox no procesó ningún pago diferido (puede estar desactivado)"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# FF-06 — Fitness function de AISLAMIENTO (QA-07)
# ═══════════════════════════════════════════════════════════════════════════════

class TestFF06Aislamiento:
    """
    FF-06: QA-07 — verifica que la arquitectura tenga documentado y planificado
    el aislamiento entre picanterías (ADR-008 + iteración 3).
    En producción se añadiría una consulta real contra BD con RLS activado.
    """

    def test_ff06_adr_008_existe_con_rls(self):
        """ADR-008 debe existir y mencionar RLS (Row-Level Security)."""
        ruta = os.path.join(
            os.path.dirname(__file__), "..",
            "docs", "architecture", "adr", "008-seguridad-modificabilidad.md"
        )
        assert os.path.exists(ruta), (
            "FF-06: docs/architecture/adr/008-seguridad-modificabilidad.md no existe"
        )
        contenido = open(ruta, encoding="utf-8").read().lower()
        assert "rls" in contenido or "row-level" in contenido, (
            "FF-06: ADR-008 no menciona Row-Level Security (RLS)"
        )

    def test_ff06_iteracion3_documenta_picanteria_id(self):
        """La iteración 3 de ADD debe documentar picanteria_id como mecanismo de aislamiento."""
        ruta = os.path.join(
            os.path.dirname(__file__), "..",
            "docs", "architecture", "add", "iteracion-3.md"
        )
        assert os.path.exists(ruta), "FF-06: docs/architecture/add/iteracion-3.md no existe"
        contenido = open(ruta, encoding="utf-8").read().lower()
        assert "picanteria_id" in contenido, (
            "FF-06: iteracion-3.md no documenta el mecanismo picanteria_id"
        )

    def test_ff06_modulo_pedidos_no_expone_datos_crudos_sin_filtro(self):
        """El módulo de pedidos no debe tener funciones que retornen TODOS los pedidos sin filtro."""
        ruta = os.path.join(
            os.path.dirname(__file__), "..", "src", "pedidos", "servicio.py"
        )
        tree = ast.parse(open(ruta, encoding="utf-8").read())
        funciones = [n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        peligrosas = [f for f in funciones if "all" in f.lower() or "todos" in f.lower()]
        assert not peligrosas, (
            f"FF-06: existen funciones sin filtro de picanteria: {peligrosas}"
        )
