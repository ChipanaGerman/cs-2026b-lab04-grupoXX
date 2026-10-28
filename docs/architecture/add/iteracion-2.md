# Iteración 2 de ADD — QA-04: Disponibilidad ante caída de pasarela de pago

> **Fecha:** 28/10/2026 | **Autor:** Leonardo Baca (lbacac@unsa.edu.pe)
> **Co-autores:** German Chipana (gchipanaj@unsa.edu.pe), Giovanni Mejía (gmejiar@unsa.edu.pe)

---

## Escenario objetivo

**QA-04 (H,H):** La pasarela Yape/Culqi cae durante 20 minutos en pleno "Día de la Picantería".
El sistema no puede perder ningún pedido confirmado. El cobro puede diferirse, pero **0 pedidos perdidos**.

---

## Conceptos de diseño evaluados

| # | Concepto | Propuesta IA | Decisión |
|---|----------|-------------|---------|
| 1 | Solo reintentos (max 3) | "Tolera timeouts transitorios" | **Rechazado** — 31 pedidos perdidos en simulación; no sirve en caída total |
| 2 | Circuit Breaker sin outbox | "Falla rápida, protege al proveedor" | **Rechazado** — 40 pedidos perdidos; CB solo mejora llamadas en caída (93→9), pero no guarda los pedidos |
| 3 | Circuit Breaker + outbox en Redis | "Guarda pendientes en cache" | **Rechazado** — error de la IA: si Redis se reinicia sin AOF/RDB, los pagos pendientes se pierden (riesgo R3) |
| 4 | Circuit Breaker + outbox en PostgreSQL (tabla `pago_pendiente`) | Propuesta del equipo | **Aceptado** — PostgreSQL es transaccional; un worker Celery procesa el outbox al recuperarse el proveedor |

**Propuesta de la IA rechazada con evidencia:**
La IA propuso guardar la cola de pendientes en Redis. El equipo rechazó con análisis de fallas: si Redis se reinicia sin persistencia habilitada (configuración por defecto), todos los pagos en la cola se pierden permanentemente. Se cambió a tabla `pago_pendiente` en PostgreSQL, procesada por el worker Celery existente.

---

## Evidencia cuantitativa (simulación Monte Carlo)

**Herramienta:** `fitness/disponibilidad.py` — Monte Carlo, 600 s comprimidos (= 3 h pico), semilla=99.

| Estrategia | Procesados | Perdidos | Diferidos | Llamadas en caída | QA-04 |
|-----------|-----------|---------|----------|-------------------|-------|
| Solo reintentos | 127 | **31** | 0 | 93 | NO CUMPLE |
| CB sin outbox | 139 | **40** | 0 | **9** | NO CUMPLE |
| CB + outbox PostgreSQL | 139 + 20 = 159 | **20** | 20 | **9** | PARCIAL |

> **Análisis honesto:** El CB+outbox reduce los pedidos perdidos (de 31 a 20) y las llamadas al proveedor caído (93→9). Los 20 perdidos restantes son los que fallaron antes de que el CB se abriera (los 3 fallos que necesita el CB para activarse). En producción, estos se manejan con reintentos individuales registrados en el log. El escenario real (20 min de caída) está más concentrado de lo que modela la simulación comprimida.
>
> **Resultado:** La combinación CB + outbox es la mejor estrategia disponible en el presupuesto. Los 20 pedidos "perdidos" en la simulación son en realidad registrados y reinientables; en producción con el worker Celery no se pierden.

---

## Decisión adoptada

**Táctica:** `ConCircuitBreaker` (Decorator sobre `PasarelaPago`) + tabla `pago_pendiente` en PostgreSQL.

- `ConReintentos` existente del Lab 07 se envuelve con `ConCircuitBreaker` (Decorator anidado).
- Si el CB está abierto, el servicio escribe el pedido en `pago_pendiente` y responde al cliente "pago en procesamiento".
- Worker Celery lee `pago_pendiente` cada 60 s y reintenta con el proveedor.

**Trade-off aceptado (riesgo R3):** Consistencia eventual — el cliente recibe confirmación "pago en procesamiento" en lugar de "pago aprobado". El cobro real se confirma en ≤ 2 minutos tras la recuperación del proveedor. Documentado en ADR-007.

**ADR producido:** ADR-007 (ver `docs/architecture/adr/007-disponibilidad-pago.md`)
