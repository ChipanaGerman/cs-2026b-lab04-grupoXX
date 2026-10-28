# Iteración 3 de ADD — QA-07 + QA-08: Seguridad y Modificabilidad

> **Fecha:** 28/10/2026 | **Autor:** Giovanni Mejía (gmejiar@unsa.edu.pe)
> **Co-autores:** German Chipana (gchipanaj@unsa.edu.pe), Leonardo Baca (lbacac@unsa.edu.pe)

---

## Escenario objetivo

**QA-07 (H,M) — Seguridad/Aislamiento:** Un repartidor autenticado como Picantería A no puede
ver los pedidos de Picantería B. 0 filas ajenas visibles en ninguna consulta.

**QA-08 (H,L) — Modificabilidad:** Agregar un nuevo distrito de reparto requiere ≤ 1 día-persona
y 0 módulos ajenos modificados.

---

## Conceptos de diseño evaluados

### QA-07 — Aislamiento entre picanterías

| # | Concepto | Propuesta IA | Decisión |
|---|----------|-------------|---------|
| 1 | Base de datos por picantería | "Aislamiento máximo" | **Rechazado** — operación compleja; no escala en VPS con 20+ picanterías |
| 2 | Esquema PostgreSQL por picantería | "Buen aislamiento" | **Rechazado para MVP** — migraciones por esquema; se revisará si hay >20 picanterías |
| 3 | Columna `picanteria_id` + Row-Level Security (RLS) + claim en JWT | Propuesta del equipo + IA | **Aceptado** — aislamiento en BD, sin lógica en el servicio; genera riesgo R2 (error de configuración RLS) |

### QA-08 — Modificabilidad

La arquitectura Modular Monolith + Ports & Adapters del Lab 07 ya resuelve QA-08:
- Agregar un distrito: insertar fila en `distrito` + configurar polígono de cobertura.
- 0 módulos de código modificados (solo datos de configuración).
- Evidencia: `test_open_closed_nuevo_medio_sin_modificar_el_servicio` del Lab 07 demuestra el principio.

**Propuesta de la IA revisada:** La IA propuso usar un sistema de plugins dinámicos para los distritos. El equipo lo rechazó: la tabla de configuración en BD es suficiente, más simple y evita la complejidad de carga dinámica de módulos.

---

## Evidencia cuantitativa

### QA-07 — Fitness function de aislamiento (análisis comparativo de alternativas)

La naturaleza de QA-07 no admite simulación estadística directa. Se evaluó con:

| Criterio | BD separadas | Esquema por picantería | `picanteria_id` + RLS |
|---------|-------------|----------------------|----------------------|
| Aislamiento | Máximo | Alto | Alto (si RLS correcto) |
| Agregar picantería | > 30 min (nueva BD) | ~5 min (migración) | < 1 min (INSERT) |
| Costo en VPS | Inviable (múltiples procesos) | Medio | Bajo |
| Riesgo de error | Bajo | Medio | **R2: configuración RLS** |
| Verificable en CI | No | Parcial | **Sí** (fitness function) |

**Decisión justificada:** `picanteria_id` + RLS es la única opción verificable automáticamente en CI (la fitness function consulta como Picantería A y exige 0 filas de Picantería B). Mitigación del riesgo R2: incluida en `tests/test_fitness.py`.

### QA-08 — Evidencia de modificabilidad (Lab 07)

La prueba `test_open_closed_nuevo_medio_sin_modificar_el_servicio` demuestra que agregar un nuevo componente (medio de pago) no requiere modificar el servicio. El mismo principio aplica a distritos de reparto.

---

## Decisión adoptada

**Táctica QA-07:** `picanteria_id` + Row-Level Security de PostgreSQL + claim `picanteria_id` en el JWT.
- El claim se valida en el middleware Django antes de toda consulta.
- Toda tabla con datos de pedidos/menús incluye la columna `picanteria_id` indexada.
- **Riesgo R2 aceptado:** Mitigado con fitness function de aislamiento en CI.

**Táctica QA-08:** Configuración en BD (tabla `distrito_reparto`) sin código adicional.
- El radio de cobertura, polígono y picantería_id asociada son configurables sin despliegue.

**Trade-offs aceptados:**
- RLS puede ralentizar consultas (~5-10 ms extra por política). Aceptable dado que p95 actual es 26 ms.
- Consistencia eventual entre la tabla de distritos y el algoritmo de asignación de repartidores.

**ADR producido:** ADR-008 (ver `docs/architecture/adr/008-seguridad-modificabilidad.md`)
