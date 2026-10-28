# ADR-008: Seguridad y Modificabilidad — RLS + configuración en BD

- **Estado:** Aceptado
- **Fecha:** 28/10/2026
- **Autor:** Giovanni Mejía (gmejiar@unsa.edu.pe)

---

## Contexto

**QA-07 (H,M):** Un repartidor autenticado como Picantería A no puede ver pedidos de Picantería B.
**QA-08 (H,L):** Agregar un nuevo distrito de reparto debe costar ≤ 1 día-persona, 0 módulos tocados.

---

## Decisión

### QA-07 — Aislamiento entre picanterías

Se adopta: columna `picanteria_id` en todas las tablas de pedidos/menús + **Row-Level Security (RLS) de PostgreSQL** + claim `picanteria_id` en el JWT validado por middleware Django.

Se rechaza "una BD por picantería" (propuesta IA): operación compleja, no escala en el VPS.
Se pospone "esquema por picantería": se revisará si hay más de 20 picanterías.

### QA-08 — Modificabilidad

Se adopta: tabla de configuración `distrito_reparto(id, nombre, poligono_cobertura, picanteria_id)`. Agregar un distrito es un INSERT, sin despliegue de código.

Se rechaza sistema de plugins dinámicos (propuesta IA): innecesariamente complejo para el MVP.

---

## Evidencia

Análisis comparativo de alternativas para QA-07 (tabla en iteracion-3.md):

| Criterio | BD separadas | Esquema/picantería | picanteria_id + RLS |
|---------|-------------|-------------------|---------------------|
| Aislamiento | Máximo | Alto | **Alto** (si RLS correcto) |
| Nueva picantería | > 30 min | ~5 min | **< 1 min** |
| Verificable en CI | No | Parcial | **Sí (FF-06)** |

---

## Consecuencias

**Positivas:**
- QA-07: aislamiento en BD, sin lógica duplicada en el servicio.
- QA-08: una nueva picantería o distrito se configura sin código.
- Ambos verificables en CI (fitness functions FF-06).

**Negativas (trade-offs):**
- **Riesgo R2:** Un error en las políticas RLS expone datos entre picanterías. Mitigación: fitness function FF-06 que consulta como Picantería A y exige 0 filas de Picantería B.
- RLS agrega ~5-10 ms por consulta. Aceptable: el presupuesto actual es 26 ms.
