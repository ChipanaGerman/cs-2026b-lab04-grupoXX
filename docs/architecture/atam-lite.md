# ATAM-lite — PicanteríaYa 2.0 (Lab 08)

> Evaluación cruzada recibida del equipo evaluador + respuestas fundamentadas del equipo.
> **Fecha:** 28/10/2026

---

## Hallazgos recibidos de la evaluación cruzada

### Punto de sensibilidad 1 (PS-1)
**Hallazgo:** El p95 de QA-01 depende fuertemente de la tasa de aciertos de la caché Redis.
Si Redis se reinicia (caché fría), el comportamiento cambia significativamente.

**Respuesta del equipo:** Confirmado por simulación. Con caché fría (0% hit), el p95 sube a
~97 ms (con índice) — aún muy por debajo del umbral de 1 000 ms. El índice garantiza el
escenario en la situación más desfavorable. Aceptamos el hallazgo; no es un riesgo crítico.

---

### Punto de sensibilidad 2 (PS-2)
**Hallazgo:** La latencia del WebSocket de GPS (QA-03: posición cada 5 s) depende del número
de repartidores activos simultáneamente. Django Channels no está modelado en la simulación.

**Respuesta del equipo:** Correcto. Django Channels usa un proceso separado con ASGI; la
simulación M/G/c modela solo requests HTTP sincrónicos. El GPS es un canal independiente.
Para el MVP (≤ 50 repartidores simultáneos), la latencia de WebSocket se estima ≤ 200 ms.
Se registra como **riesgo R5** (no modelado en la simulación actual).

---

### Punto de trade-off 1 (TT-1)
**Hallazgo:** La caché Redis mejora el rendimiento (QA-01) pero puede mostrar stock
desactualizado (correctitud). Un cliente podría ver un plato "disponible" que ya se agotó.

**Respuesta del equipo:** Trade-off conocido y aceptado. Mitigación: validar stock real en
la transacción de confirmación (antes de cobrar), nunca en la visualización del menú.
Si el stock está agotado al confirmar, se notifica al cliente antes del cobro. TTL = 30 s
es un equilibrio razonable: máximo 30 s de desfase vs reducción de carga en BD.

---

### Punto de trade-off 2 (TT-2)
**Hallazgo:** El Circuit Breaker (QA-04) protege al proveedor caído pero introduce
consistencia eventual: el cliente no sabe inmediatamente si su pago fue aprobado.

**Respuesta del equipo:** Trade-off documentado en ADR-007. La experiencia del cliente
es "pago en procesamiento" (≤ 2 minutos de espera). Aceptable para el MVP; el usuario
recibe WhatsApp de confirmación al procesarse el outbox.

---

### Riesgo R1 (evaluador externo)
**Hallazgo:** Un solo VPS es punto único de falla para QA-03 y QA-05 (disponibilidad).
**Probabilidad:** 3/5 | **Impacto:** 4/5

**Respuesta del equipo:** Aceptado para el MVP dentro del presupuesto ($20/mes).
Mitigación parcial: supervisor de procesos (systemd) reinicia el proceso en ≤ 30 s (QA-05 cumplido).
Plan de recuperación ante desastre: respaldo diario en DigitalOcean Spaces; restauración en ≤ 2 h.
ADR-009 pendiente para documentar el plan de DR formal.

---

### Riesgo R2 (propio — detectado en iteración 3)
**Hallazgo:** Un error en las políticas RLS de PostgreSQL expone datos entre picanterías.
**Probabilidad:** 2/5 | **Impacto:** 5/5

**Respuesta del equipo:** Mitigado con fitness function FF-06 (consulta como Picantería A,
exige 0 filas de Picantería B). La fitness function se ejecuta en cada PR vía GitHub Actions.

---

### Riesgo R3 (evaluador externo)
**Hallazgo:** El outbox de pagos perdería datos si Redis se reinicia.
**Probabilidad:** 3/5 | **Impacto:** 5/5

**Respuesta del equipo:** Este riesgo motivó el cambio a PostgreSQL (ADR-007).
El outbox en Redis fue propuesto por la IA y **rechazado** exactamente por este motivo.
El outbox en PostgreSQL es transaccional y sobrevive a reinicios.

---

### Riesgo R4 (propio — caché)
**Hallazgo:** Stock desactualizado durante TTL = 30 s.
**Probabilidad:** 4/5 | **Impacto:** 2/5

**Respuesta del equipo:** Impacto bajo (experiencia de usuario, no pérdida de datos).
Mitigado con validación de stock en la transacción de confirmación (ver ADR-006).

---

### Riesgo R5 (propio — WebSocket GPS no modelado)
**Hallazgo:** La simulación no modela Django Channels ni el número de conexiones WebSocket.
**Probabilidad:** 3/5 | **Impacto:** 3/5

**Respuesta del equipo:** Riesgo aceptado para el MVP. Se agrega a la lista de deuda técnica.
Mitigación futura: prueba de carga con k6 WebSocket en un sprint posterior.

---

### No riesgo 1
**Hallazgo del evaluador:** "El monolito modular no soportará el Día de la Picantería."
**Respuesta del equipo:** Refutado con evidencia. La simulación M/G/c muestra p95 = 219 ms
a 10× carga, muy por debajo del umbral de 4 000 ms. El monolito modular es suficiente.

### No riesgo 2
**Hallazgo:** "Celery no escalará para la campaña."
**Respuesta del equipo:** Falso positivo. El worker Celery procesa el outbox de pagos pendientes
(máximo 20 pagos en 20 minutos de caída). A 3 pagos/minuto por worker, un solo worker alcanza
y sobra. La IA no tenía evidencia de este "riesgo"; se solicitó y no la proporcionó.

---

## Matriz de probabilidad × impacto

| Riesgo | Probabilidad (1-5) | Impacto (1-5) | Score | Zona | Mitigación |
|--------|-------------------|--------------|-------|------|-----------|
| R1 — VPS único punto falla | 3 | 4 | 12 | **Alta** | Systemd + respaldo diario; plan DR |
| R2 — Error RLS | 2 | 5 | 10 | **Alta** | Fitness function FF-06 en CI |
| R3 — Outbox en Redis | 1 | 5 | 5 | Media | Resuelto: outbox en PostgreSQL |
| R4 — Stock desactualizado | 4 | 2 | 8 | Media | Validación en confirmación |
| R5 — WebSocket no modelado | 3 | 3 | 9 | Media | Deuda técnica; k6 en próximo sprint |
