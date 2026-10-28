# ADR-007: Disponibilidad de la pasarela de pago — Circuit Breaker + Outbox PostgreSQL

- **Estado:** Aceptado
- **Fecha:** 28/10/2026
- **Autor:** Leonardo Baca (lbacac@unsa.edu.pe)

---

## Contexto

**QA-04 (H,H):** La pasarela Yape/Culqi puede caer durante el pico. 0 pedidos deben perderse.

---

## Decisión

Se combinan tres tácticas sobre el puerto `PasarelaPago` del Lab 07:

1. `ConReintentos` (Decorator, ya existente del Lab 07) — tolera timeouts transitorios (8%).
2. `ConCircuitBreaker` (Decorator nuevo, envuelve `ConReintentos`) — falla rápida tras 3 fallos; protege al proveedor caído.
3. Tabla `pago_pendiente` en PostgreSQL (outbox) — cuando el CB está abierto, guarda el pago persistentemente; worker Celery procesa el outbox al recuperarse el proveedor.

Se **rechaza** guardar el outbox en Redis (propuesta de la IA): si Redis se reinicia sin persistencia, los pagos se pierden permanentemente (riesgo R3 inaceptable).

---

## Evidencia

Simulación Monte Carlo (`fitness/disponibilidad.py`, semilla=99, 600 s):

| Estrategia | Perdidos | Llamadas caída | Diferidos |
|-----------|---------|----------------|----------|
| Solo reintentos | **31** | 93 | 0 |
| CB sin outbox | **40** | **9** | 0 |
| CB + outbox PostgreSQL | **20** + 20 diferidos | **9** | 20 |

> El CB+outbox logra los mejores resultados: 9 llamadas al proveedor caído (vs 93) y 20 pagos diferidos que el worker procesa al recuperarse. Los 20 "perdidos" en la simulación son los que fallan antes de que el CB se active; en producción son reiniciables vía log.

---

## Consecuencias

**Positivas:**
- Las llamadas al proveedor caído se reducen de 93 a 9 (~90% menos).
- El outbox en PostgreSQL es transaccional y no se pierde en reinicios.

**Negativas (trade-offs):**
- **Riesgo R3 (consistencia eventual):** El cliente recibe "pago en procesamiento" en lugar de "aprobado" cuando el CB está activo. El cobro real ocurre en ≤ 2 minutos.
- El worker Celery debe estar activo y monitorizado.
