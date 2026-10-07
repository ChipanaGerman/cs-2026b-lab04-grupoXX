# Bitácora de interacciones con IA — Lab 05

> **Caso:** PicanteríaYa | **Regla de oro:** La IA propone, el equipo decide y verifica.
> Nunca se ingresaron datos personales o confidenciales en ningún prompt.

---

## Interacción 1 — Diagrama de clases inicial

| Campo | Detalle |
|-------|---------|
| **Fecha** | 2026-10-07 |
| **Herramienta** | Claude (Anthropic) |
| **Tipo** | Ingeniería directa — Prompt IA 1 |
| **Prompt** | "Actúa como diseñador de software orientado a objetos. Contexto: módulo Pedidos y Pagos de un monolito modular (ADR-001: puertos y adaptadores para integraciones externas). Historia: HU-01 PicanteríaYa — pedir el menú del día y pagar con Yape. Criterios de aceptación: [CA-01, CA-02, CA-03]. Tarea: genera un diagrama de clases en PlantUML con atributos tipados, operaciones, multiplicidades, una enumeración para el estado del pedido y una interfaz (puerto) para la pasarela de pagos. Formato: solo el código PlantUML." |
| **Propuesta de la IA** | Generó el diagrama con clases: Cliente, Pedido, LineaPedido, Plato, Pago, PasarelaPago (interfaz). Incluyó `EstadoPedido` como enum. |
| **Verificación** | Faltaba la clase `Menu`, la relación `Picanteria`—`Menu` y los puertos `ColaMensajes` y `Notificador`. El adaptador `YapeAdapter` usaba herencia en lugar de realización de la interfaz. |
| **Decisión** | Rechazada parcialmente. Se corrigió: (1) se agregaron `Menu`, `Picanteria`, `Repartidor`; (2) se modeló `CulqiYapeAdapter` como realizador del puerto `PasarelaPago`; (3) se agregaron `ColaMensajes` y `Notificador` como puertos adicionales. |

---

## Interacción 2 — Refinamiento del diagrama de clases

| Campo | Detalle |
|-------|---------|
| **Fecha** | 2026-10-07 |
| **Herramienta** | Claude (Anthropic) |
| **Tipo** | Refinamiento iterativo |
| **Prompt** | "Agrega al diagrama anterior: (1) la clase Menu con relación de composición con Plato; (2) la clase Picanteria que publica menus; (3) la clase Repartidor con atributos de geolocalización; (4) un puerto ColaMensajes para la cola Redis/Celery. Mantén el estilo PlantUML y la consistencia con el ADR-001." |
| **Propuesta de la IA** | Agregó las clases solicitadas. Modeló `Repartidor` con relación de dependencia directa hacia `Pedido`. |
| **Verificación** | La dependencia `Repartidor → Pedido` en el diagrama de clases viola el ADR-001: el módulo repartidores no debe conocer directamente al módulo pedidos. La asignación es asíncrona vía cola. |
| **Decisión** | Corregida: se eliminó la dependencia directa `Repartidor → Pedido` del diagrama de clases y se mantuvo solo la relación de asignación a través del puerto `ColaMensajes`. |

---

## Interacción 3 — Diagrama de secuencia

| Campo | Detalle |
|-------|---------|
| **Fecha** | 2026-10-07 |
| **Herramienta** | Claude (Anthropic) |
| **Tipo** | Ingeniería directa — Prompt IA 1 adaptado |
| **Prompt** | "Genera un diagrama de secuencia PlantUML para el flujo 'pedir el menú del día y pagar con Yape' de PicanteríaYa. Participantes: Cliente, App/PWA, PedidoController, ServicioPedidos, RepositorioPedidos, Pedido, PasarelaPago (CulqiYapeAdapter), ColaMensajes, Notificador. Incluye: fragmento loop para las líneas, fragmento alt para pago aprobado/rechazado, al menos un mensaje asíncrono para la cola. Solo el código PlantUML." |
| **Propuesta de la IA** | Generó el diagrama con los participantes y fragmentos solicitados. |
| **Verificación (C1)** | El mensaje `encolarAsignacionRepartidor` se enviaba a `ColaMensajes` pero esta interfaz no tenía la operación declarada en el diagrama de clases. Se corrigió agregando el método al diagrama de clases. |
| **Decisión** | Aceptada con corrección. Se actualizó `clases.puml` para agregar la operación `encolarAsignacionRepartidor` a la interfaz `ColaMensajes`. |

---

## Interacción 4 — Esqueleto de código Python

| Campo | Detalle |
|-------|---------|
| **Fecha** | 2026-10-07 |
| **Herramienta** | Claude (Anthropic) |
| **Tipo** | Ingeniería directa — Prompt IA 2 |
| **Prompt** | "Genera el esqueleto en Python 3.10+ (dataclasses y type hints) del siguiente diagrama de clases. Respeta exactamente los nombres de clases, atributos y operaciones (en snake_case), las enumeraciones, las interfaces como clases abstractas (ABC) y las multiplicidades. Implementa solo la lógica mínima de las operaciones de Pedido; los adaptadores deben lanzar NotImplementedError. [diagrama clases.puml]" |
| **Propuesta de la IA** | Generó `dominio.py` con dataclasses, enums y ABCs. Usó nombres en snake_case correctamente. Incluyó `ServicioPedidos` como clase concreta. |
| **Verificación** | Faltaba la validación de multiplicidad `1..*` en `Pedido.confirmar()` (regla C3). Los adaptadores solo tenían el método requerido pero no el docstring que explica la integración pendiente. |
| **Decisión** | Aceptada con corrección. Se agregó: (1) validación `if not self.lineas` en `confirmar()`; (2) docstrings explicativos en los adaptadores; (3) se verificó que todos los métodos del diagrama UML tuvieran su equivalente en Python. |

---

## Interacción 5 — Auditor de consistencia

| Campo | Detalle |
|-------|---------|
| **Fecha** | 2026-10-07 |
| **Herramienta** | Claude (Anthropic) |
| **Tipo** | Revisión de consistencia — Prompt IA 3 |
| **Prompt** | "Actúa como revisor de diseño. Te paso cinco diagramas UML en PlantUML/Mermaid de PicanteríaYa: [clases.puml, secuencia-pedir-pagar.puml, estados-pedido.mmd, actividades-asignacion-repartidor.puml, paquetes.puml]. Verifica estas reglas y responde en una tabla (regla, elemento, problema, corrección sugerida): C1 cada mensaje de secuencia es una operación de la clase receptora; C2 cada transición de estados corresponde a una operación de la clase; C3 multiplicidades coherentes; C4 paquetes sin ciclos; C5 nombres consistentes. No reescribas los diagramas; solo reporta hallazgos." |
| **Propuesta de la IA** | Generó tabla con 5 hallazgos: C1 (ColaMensajes sin operación), C2 (transición sin operación), C3 (sin validación de 1..*), C4 (supuesto ciclo indirecto), C5 (snake_case vs. camelCase). |
| **Verificación** | El hallazgo C4 fue un **falso positivo**: la IA confundió una cadena de dependencias unidireccional con un ciclo. Los demás hallazgos fueron verdaderos positivos y se corrigieron. |
| **Decisión** | C1, C2, C3 y C5 aceptados y corregidos. C4 rechazado y documentado como falso positivo con justificación en `consistencia.md`. |
