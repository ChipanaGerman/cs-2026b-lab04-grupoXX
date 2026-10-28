# ADR-006: Tácticas de rendimiento — Índice + Caché Redis (QA-01, QA-02)

- **Estado:** Aceptado
- **Fecha:** 28/10/2026
- **Autores:** German Chipana (gchipanaj@unsa.edu.pe)
- **Co-autores:** Leonardo Baca, Giovanni Mejía

---

## Contexto

Escenario de crecimiento Lab 08: "Día de la Picantería" — 10× más pedidos en 3 horas.

**QA-01:** 400 clientes consultan el menú simultáneamente → p95 ≤ 1 s.
**QA-02:** 4 000 pedidos/hora en pico → p95 confirmación ≤ 4 s, 0 perdidos.

La arquitectura actual (monolito modular + 4 workers Gunicorn) no tiene índices ni caché en el endpoint de menú.

---

## Decisión

Se adoptan dos tácticas del catálogo de Bass et al. (2021) aplicadas sobre el módulo `menu`:

1. **Índice** en `plato(picanteria_id, activo)` — táctica "optimizar consultas".
2. **Caché Redis** con TTL = 30 s para el menú del día — táctica "caché".

Se **rechaza** escalar a microservicios + Kubernetes (propuesta de la IA): la simulación demuestra que no es necesario con el presupuesto actual.

---

## Evidencia

Simulación M/G/c (`fitness/rendimiento.py`, semilla=42, 300 s):

| Táctica | p95 QA-01 (pico) | p95 QA-02 (10×) | ¿Cumple? |
|---------|----------------|----------------|---------|
| Sin tácticas | 97 ms | 97 ms | Sí (margen) |
| Índice + caché (85% hit) | **26 ms** | **219 ms** | ✅ Sí |

---

## Consecuencias

**Positivas:**
- p95 muy por debajo del umbral: 26 ms vs 1 000 ms (QA-01), 219 ms vs 4 000 ms (QA-02).
- Costo casi nulo: migración de 1 línea para el índice; Redis ya está en la infraestructura (Celery).

**Negativas (trade-offs):**
- **Riesgo R4 (stock desactualizado):** La caché puede mostrar un plato agotado hasta 30 s. Mitigación: validar stock al confirmar el pedido, nunca al mostrar el menú.
- Si Redis se reinicia (caché fría), el p95 sube a ~97 ms (aún ≤ 1 s gracias al índice).

**Plan B documentado:** Si la carga supera 8 000 pedidos/hora (×20), escalar a 8 workers en un segundo VPS (~$40/mes total).
