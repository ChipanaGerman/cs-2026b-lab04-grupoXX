# Iteración 1 de ADD — PicanteríaYa 2.0
# Objetivo: QA-01 (Rendimiento menú) y QA-02 (Confirmación pedido "Día de la Picantería")

> **Escenario de crecimiento:** "Día de la Picantería" — 10× más pedidos en 3 horas,
> seguimiento del repartidor cada 5 segundos.
>
> **Fecha:** 28/10/2026 | **Autor:** German Chipana (gchipanaj@unsa.edu.pe)
> **Co-autores:** Leonardo Baca (lbacac@unsa.edu.pe), Giovanni Mejía (gmejiar@unsa.edu.pe)

---

## Entradas de esta iteración

| Insumo | Origen | Qué aporta |
|--------|--------|-----------|
| Plazo 1 mes, presupuesto VPS ~$20/mes, 3 developers Python/Django | `drivers.md` | Restricciones duras |
| Monolito Modular + Redis/Celery | ADR-001 (Lab 04) | Punto de partida; no cambiar sin evidencia |
| Módulos `pedidos`, `menu`, `repartidores`, `notificaciones` | workspace.dsl (Lab 06) | Componentes actuales |
| Strategy + Adapter + Factory + Decorator + Observer | ADR-005 (Lab 07) | Base para agregar tácticas sin reescribir |

## Escenarios objetivo (H,H) y (H,M)

| ID | Escenario | Calificación |
|----|-----------|-------------|
| **QA-01** | 400 clientes consultan menú simultáneamente → p95 ≤ 1 s | **(H,H)** |
| **QA-02** | 10× pedidos en 3 h → p95 confirmación ≤ 4 s, 0 perdidos | **(H,H)** |

---

## Paso 2: Árbol de utilidad — corrección del equipo frente a la IA

**Prompt IA 1 usado:** "Actúa como arquitecto. Contexto: [drivers.md, ADR-001, escenario Día Picantería]. Propón escenarios de calidad con medidas numéricas y calificación (H/M/L). No propongas soluciones todavía."

**Corrección del equipo:**
La IA calificó QA-06 (datos personales) como **(H,H)**. El equipo lo bajó a **(M,L)** porque:
- HTTPS ya está activo en el VPS (certificado Let's Encrypt).
- El disco del VPS tiene cifrado en reposo (DigitalOcean feature activo).
- No hay nuevas organizaciones que compartan datos; el cambio del escenario no afecta este atributo.

---

## Paso 3: Conceptos de diseño evaluados

**Prompt IA 2 usado:** "Para QA-01 y QA-02, propón 4 conceptos de diseño del catálogo de Bass et al. Respeta ADR-001 (monolito modular VPS). Indica qué mejora, qué empeora, costo y complejidad."

| # | Concepto de diseño | Propuesta IA | Decisión del equipo |
|---|-------------------|-------------|-------------------|
| 1 | Migrar a microservicios + Kubernetes | "Escalabilidad horizontal para el día pico" | **Rechazado** — viola plazo y presupuesto; la simulación muestra que no es necesario |
| 2 | Escalar de 4 a 8 workers Gunicorn (segundo VPS) | "Plan B si hay saturación" | **Pendiente** — viable pero duplica costo (~$40/mes); queda como plan B documentado |
| 3 | Índice en `plato.picanteria_id` + `plato.activo` | "Optimizar consultas" | **Aceptado** — costo casi nulo (migración de 1 línea); efecto medible |
| 4 | Caché del catálogo en Redis (TTL = 30 s) | "Táctica caché para el menú del día" | **Aceptado como complemento** — reduce carga en BD; genera riesgo R4 (stock desactualizado) |

**Propuesta rechazada con argumento:**
La IA propuso microservicios porque "es la solución estándar para 10× carga". El equipo rechazó con evidencia: la simulación M/G/c muestra que con índice + caché, el p95 a 10× carga es **< 300 ms**, muy por debajo del umbral de 4 s, con solo 4 workers.

---

## Paso 4: Evidencia cuantitativa (simulación M/G/c)

**Herramienta:** `fitness/rendimiento.py` — simulación M/G/c con llegadas Poisson, 4 workers, 300 segundos.

### Resultados reales (salida del script)

| Escenario | Carga (req/s) | Táctica | p95 (ms) | Utilización | ¿Cumple? |
|-----------|-------------|---------|---------|-------------|---------|
| QA-01 normal | 50/h = 0.014 | Con caché (85% hit) | **6 ms** | 0.0% | ✅ ≤ 1 s |
| QA-01 pico domingos | 400/h = 0.111 | Con caché (85% hit) | **26 ms** | 0.0% | ✅ ≤ 1 s |
| QA-02 Día Picantería — SIN tácticas | 4000/h = 1.11 | Ninguna (sin índice) | **97 ms** | 2.2% | ✅ ≤ 4 s |
| QA-02 Día Picantería — CON tácticas | 4000/h = 1.11 | Índice + caché | **219 ms** | 4.1% | ✅ ≤ 4 s |

> **Hallazgo que corrige a la IA:** Con solo caché (sin índice), el sistema es sensible a la tasa de aciertos del caché. Si Redis se reinicia (caché frío, 0% hit), el p95 sube a ~97 ms (con índice) o hasta ~250 ms (sin índice). Por eso se adoptan **ambas tácticas**: el índice garantiza el escenario en caché fría, y la caché da margen en condiciones normales.

### Supuestos de la simulación

1. **Llegadas:** Poisson (exponencial entre llegadas). Real: puede haber ráfagas; la simulación es optimista.
2. **Workers:** 4 Gunicorn sincrónicos. Django Channels para WebSocket GPS no está modelado aquí.
3. **Tiempos de servicio:** Gaussianos con medias calibradas del MVP. Real: lognormal; estimamos conservadoramente.
4. **Tasa de aciertos caché:** 85% para menú del día (plato popular, TTL 30 s).
5. **Red:** Se ignora latencia cliente-servidor (~20-50 ms en 4G arequipeño).

---

## Decisión adoptada

**Táctica seleccionada:** Índice en `plato.picanteria_id` + caché Redis con TTL = 30 s.

- **Trade-off aceptado (riesgo R4):** La caché puede mostrar un plato agotado durante hasta 30 s. Mitigación: validar stock en la transacción de confirmación (nunca en la visualización del menú).
- **Escenario cumplido:** QA-01 (p95 = 26 ms ≤ 1 s) y QA-02 (p95 = 219 ms ≤ 4 s). ✅
- **ADR producido:** ADR-006 (ver `docs/architecture/adr/006-tacticas-rendimiento.md`)

---

*Generado en iteración 1 de ADD 3.0 · PicanteríaYa Lab 08*
