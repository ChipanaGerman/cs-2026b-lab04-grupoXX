# Bitácora de uso de IA — Lab 06 (Modelo C4) — PicanteríaYa

> **E7 — Lab 06** | Regla de oro: la IA propone, el equipo decide y verifica.

---

## Interacción 1 — Borrador del modelo en Structurizr DSL

| Campo | Detalle |
|-------|---------|
| **Fecha** | 2026-10-15 |
| **Herramienta** | Claude (Anthropic) |
| **Prompt (resumen)** | Actúa como arquitecto experto en C4 y Structurizr DSL. Contexto: inventario.md de PicanteríaYa (3 personas, 7 contenedores, 5 módulos) y ADR-001 (monolito modular Django, Celery, PostgreSQL, Redis, ~$20/mes VPS). Escribe un workspace.dsl completo con vistas systemContext, container, component, dynamic (pedir y pagar) y deployment. Usa solo tecnologías del ADR-001. No confundas contenedor C4 con Docker. |
| **Propuesta de la IA** | workspace.dsl con 3 personas, sistema PicanteríaYa, 5 contenedores, 5 componentes, 4 vistas. Incluyó un contenedor llamado "Nginx" como proxy dentro del sistema. |
| **Verificación del equipo** | Nginx es infraestructura de red, no un componente de negocio → va en el nodo de despliegue como DeploymentNode, no como contenedor C4. Además el ADR-001 no lo menciona explícitamente. |
| **Decisión** | Rechazado y eliminado. Se reemplazó por el nodo VPS → Docker Compose en la vista de despliegue. |

---

## Interacción 2 — Detección de sistemas externos mal modelados

| Campo | Detalle |
|-------|---------|
| **Fecha** | 2026-10-15 |
| **Herramienta** | Claude (Anthropic) |
| **Prompt (resumen)** | En el borrador de workspace.dsl la IA modeló "Culqi" como contenedor interno de PicanteríaYa. Explica por qué es incorrecto y cómo corregirlo. |
| **Propuesta de la IA** | "Culqi debe ser un softwareSystem con la etiqueta 'Externo' porque no lo construimos ni desplegamos. Está fuera del límite del sistema PicanteríaYa." |
| **Verificación del equipo** | Correcto. El ADR-001 dice explícitamente: 'usaremos Culqi como intermediario (R-05); no accedemos directamente a Yape porque no tiene API pública'. Culqi es un sistema externo. |
| **Decisión** | Aceptado. Culqi, Google Maps API y WhatsApp/FCM se modelaron como softwareSystem con etiqueta "Externo". |

---

## Interacción 3 — Auditoría C4 (Prompt IA 2)

| Campo | Detalle |
|-------|---------|
| **Fecha** | 2026-10-15 |
| **Herramienta** | Claude (Anthropic) |
| **Prompt (resumen)** | Actúa como revisor de diagramas C4. Evalúa estas vistas de PicanteríaYa con la lista de revisión de c4model.com (generales, elementos, relaciones). Responde en tabla (vista, pregunta, cumple sí/no, evidencia, corrección). No inventes problemas. |
| **Propuesta de la IA** | 5 hallazgos: (1) relación api→cola tiene dos intenciones, (2) relaciones persona→sistema sin protocolo, (3) módulo Repartidores no conectado a Google Maps, (4) puertos no indicados, (5) leyenda presente en todas las vistas. |
| **Verificación del equipo** | (1) Verdadero positivo → se mejoró la etiqueta. (2) **Falso positivo**: en nivel 1 no se requieren protocolos para personas. (3) Error de la IA: la relación SÍ existe en el modelo. (4) Parcialmente válido: no obligatorio en C4 pero se documenta en ADR. (5) Correcto. |
| **Decisión** | Se corrigió (1). Se rechazó (2) como falso positivo documentado. Se rechazó (3) por error de análisis. Se documentó (4) en ADR-001. |

---

## Interacción 4 — Explicación para público no técnico (Prompt IA 3)

| Campo | Detalle |
|-------|---------|
| **Fecha** | 2026-10-15 |
| **Herramienta** | Claude (Anthropic) |
| **Prompt (resumen)** | Explica el diagrama de contexto de PicanteríaYa al dueño de una picantería arequipeña que no es técnico. Máximo 120 palabras. Evita jerga técnica. [se pegó la vista de contexto] |
| **Propuesta de la IA** | Texto de 134 palabras con menciones a "API REST" y "base de datos PostgreSQL". |
| **Verificación del equipo** | Supera las 120 palabras y usa términos técnicos inapropiados para el público objetivo. Se reescribió eliminando "API", "PostgreSQL", "Redis", "HTTPS". Se verificó que cada afirmación correspondía a un elemento del modelo. |
| **Decisión** | Reescrito y reducido a 112 palabras. Guardado en explicacion.md. |

---

## Interacción 5 — Vista dinámica: secuencia de pasos

| Campo | Detalle |
|-------|---------|
| **Fecha** | 2026-10-15 |
| **Herramienta** | Claude (Anthropic) |
| **Prompt (resumen)** | Tomando el diagrama de secuencia del Lab 05 (flujo pedir menú y pagar con Yape), extrae una vista dynamic de Structurizr DSL con 6 a 8 pasos entre contenedores y componentes. Cada paso debe usar relaciones ya declaradas en el modelo. |
| **Propuesta de la IA** | 8 pasos entre pwa, modMenu, modPedidos, modPagos, culqi, modRepartidores, cola, modNotificaciones. Usó algunos identificadores incorrectos (`api.pedidos` en lugar de `picanteriaYa.api.modPedidos`). |
| **Verificación del equipo** | Los identificadores se corrigieron según la sintaxis `!identifiers hierarchical`. Los pasos se verificaron uno a uno contra las relaciones declaradas en el bloque `model`. Todos los pasos son coherentes con el diagrama de secuencia del Lab 05. |
| **Decisión** | Aceptado con corrección de identificadores. El resultado son 8 pasos coherentes con la secuencia UML del Lab 05. |
