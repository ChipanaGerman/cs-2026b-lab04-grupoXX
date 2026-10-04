# Bitácora de uso de IA — PicanteríaYa

> **Regla de oro:** La IA propone, el equipo decide y verifica. Todo uso de IA queda registrado aquí.  
> Al menos una interacción debe tener decisión **"Rechazada"** o **"Corregida"** con evidencia de verificación.

---

## Tabla de interacciones

| # | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|---|-------|-------------|-----------------|-------------------|------------------------------|---------|
| 1 | 29/09/2026 | Claude 3.5 Sonnet | "Actúa como arquitecto. Sistema: PicanteríaYa, delivery de picanterías arequipeñas con clientes, picantería y repartidor. MVP en 1 mes, 3 developers, VPS bajo costo. Atributo crítico: escalabilidad, pico ×8 domingos 12–15h (400 pedidos/hora). Propón 3 estilos arquitectónicos distintos con ventajas y desventajas." | Propuso: (A) Microservicios + Kubernetes, (B) Monolito en capas, (C) Monolito modular con cola. Argumentó que Kubernetes es necesario para escalar a 400 pedidos/hora de forma independiente por servicio. | El equipo calculó: 400 pedidos/hora = ~6.7 pedidos/minuto. Kubernetes requiere conocimientos DevOps avanzados que el equipo no posee (R-02) y costos de nube elevados (R-03). Un monolito con cola asíncrona puede procesar 6.7 pedidos/min sin dificultad. La IA exageró la necesidad de microservicios. | **Rechazada** (Kubernetes); se mantuvo el monolito modular con cola (C) |
| 2 | 29/09/2026 | Claude 3.5 Sonnet | "Del monolito modular con cola que recomendaste, actúa como arquitecto adversarial: ¿qué supuestos no se cumplen con nuestras restricciones (1 mes, 3 devs, bajo presupuesto, VPS único)? Enumera los 5 riesgos más graves y para cada uno una táctica de mitigación." | Listó como riesgo #3: "La integración directa con Yape API puede fallar si el endpoint cambia". Asumió que Yape tiene una API REST pública disponible para integraciones directas. | Se verificó en la documentación oficial de Yape (yape.com.pe/desarrolladores) y en foros de desarrollo peruano (foro de devs-pe en Discord): **Yape no ofrece API pública abierta para integración directa**. La integración requiere un proveedor de pagos intermediario con acuerdo comercial (Culqi, Niubiz o PayU). El riesgo real es el costo y el tiempo de onboarding del proveedor. | **Corregida**: se actualizó R-05 en drivers.md y se modificó el ADR-001 para especificar Culqi/Niubiz como capa intermediaria |
| 3 | 30/09/2026 | ChatGPT-4o | "Genera el código Mermaid para un diagrama de arquitectura de un sistema de delivery llamado PicanteríaYa, con arquitectura monolito modular, módulos: Menú, Pedidos, Pagos, Repartidores, Notificaciones. Actores: Cliente, Picantería, Repartidor. Servicios externos: Yape, Google Maps, WhatsApp." | Generó un diagrama Mermaid con sintaxis `graph LR` y flechas correctas. Sin embargo, usó `subgraph` sin nombre interno en algunos nodos, causando error de sintaxis al renderizar en mermaid.live. Además omitió el nodo de Redis/cola asíncrona, que es parte central de la arquitectura. | Se validó el código en https://mermaid.live: reportó error en línea 12 (subgraph sin ID). Se corrigió la sintaxis y se añadió el nodo `COLA["🔴 Cola Redis + Workers Celery"]` con las conexiones correspondientes desde el módulo Pedidos. | **Corregida**: se añadió el nodo de cola y se corrigió la sintaxis |
| 4 | 30/09/2026 | Claude 3.5 Sonnet | "Redacta un ADR para la decisión de usar WebSocket en lugar de HTTP polling para el seguimiento GPS de repartidores en PicanteríaYa. El contexto incluye hasta 400 pedidos simultáneos en pico dominical." | Redactó el ADR con estructura correcta (Contexto, Alternativas, Decisión, Consecuencias). Sin embargo, en las consecuencias negativas mencionó que "Django Channels requiere un servidor WebSocket separado como socket.io", lo cual es incorrecto. | Se verificó en la documentación oficial de Django Channels (channels.readthedocs.io): Django Channels usa `daphne` o `uvicorn` como servidor ASGI integrado al proyecto Django; **no requiere un servidor WebSocket externo separado ni socket.io** (que es de Node.js). La IA confundió ecosistemas. | **Corregida**: se eliminó la mención a socket.io del ADR-003 y se especificó correctamente `daphne`/`uvicorn` |
| 5 | 01/10/2026 | Gemini 1.5 Pro | "Ayúdame a redactar el escenario de calidad QA-01 de escalabilidad para PicanteríaYa. El pico es de 400 pedidos/hora los domingos 12–15h." | Redactó el escenario con las 6 partes. En la Medida propuso: "el sistema debe responder en menos de 2 segundos". Sin incluir percentil ni condición de 0 pedidos perdidos. | Un escenario de calidad sin percentil estadístico (p50, p95, p99) no es verificable: un solo pedido lento haría fallar la prueba. Se consultó la plantilla de Bass et al. (2021) de los apuntes del curso: la medida debe especificar percentil. Se añadió "p95 ≤ 4 s" y la condición "0 pedidos rechazados por sobrecarga". | **Corregida**: se actualizó QA-01 en drivers.md con medida específica y percentil |

---

## Anexo: prompts completos

### Prompt 1 — Tres alternativas arquitectónicas (entrada #1)

```
Actúa como arquitecto de software senior con experiencia en sistemas de delivery.

El sistema se llama PicanteríaYa: una plataforma de delivery de picanterías arequipeñas. Los actores son: Cliente (hace pedidos vía web o app), Picantería (publica su menú y gestiona pedidos) y Repartidor (recibe pedidos asignados y actualiza su posición GPS).

Funcionalidades del MVP:
- Menú del día por picantería
- Pedido y pago con Yape
- Asignación automática de repartidor
- Seguimiento en tiempo real del repartidor en el mapa

Restricciones:
- El MVP debe estar en producción en 1 mes
- El equipo son 3 developers con experiencia en Python/Django y JavaScript; sin experiencia en DevOps avanzado
- Presupuesto bajo: un solo VPS en la nube (~$20/mes); no podemos costear múltiples servicios gestionados
- La integración con Yape requiere un proveedor intermediario (no hay API pública directa)

Atributo de calidad crítico: ESCALABILIDAD
Los domingos de 12:00 a 15:00, los pedidos se multiplican por 8 respecto al flujo base (~50 pedidos/hora), alcanzando hasta 400 pedidos/hora. La arquitectura debe absorber este pico.

Propón 3 estilos arquitectónicos diferentes y distintos entre sí. Para cada uno indica:
1. Nombre del estilo
2. Descripción de cómo se organizaría PicanteríaYa con ese estilo (2-3 líneas)
3. Ventajas en este contexto específico
4. Desventajas o riesgos en este contexto
```

### Prompt 2 — Crítica adversarial (entrada #2)

```
Del monolito modular con cola de mensajes que recomendaste para PicanteríaYa, actúa ahora como arquitecto adversarial.

Nuestras restricciones son:
- 1 mes de plazo para el MVP
- 3 developers sin experiencia en DevOps avanzado
- VPS único de bajo costo (~$20/mes)
- Sin API pública de Yape (requiere proveedor intermediario)
- Pico dominical de 400 pedidos/hora (×8 del flujo base)

Preguntas:
1. ¿Qué supuestos estás asumiendo que podrían no cumplirse con nuestras restricciones?
2. ¿Qué podría fallar en producción específicamente durante el pico del domingo?
3. ¿Qué costo oculto tiene que no mencionaste?
Enumera los 5 riesgos más graves y, para cada uno, una táctica arquitectónica de mitigación concreta.
```

### Prompt 3 — Diagrama Mermaid (entrada #3)

```
Genera el código Mermaid para un diagrama de arquitectura (flowchart TB) del sistema PicanteríaYa.

Arquitectura: Monolito Modular con cola de mensajes Redis/Celery.

Elementos a incluir:
- Actores: Cliente (app web/PWA), Picantería (panel web), Repartidor (app móvil)
- Módulos: Menú y Catálogo, Pedidos, Pagos, Repartidores/GPS, Notificaciones
- Capa de infraestructura con repositorios y adaptadores externos
- Cola Redis + Workers Celery (para procesamiento asíncrono del pico dominical)
- Base de datos: PostgreSQL (con esquema por módulo)
- Caché: Redis (caché de menús)
- Servicios externos: Culqi/Niubiz (pasarela Yape), Google Maps API, FCM/WhatsApp API

Usa subgraph para agrupar el monolito y los módulos. Añade classDef para colorear: actores en azul, módulos en naranja, externos en morado, base de datos en verde.
```

### Prompt 4 — ADR WebSocket (entrada #4)

```
Redacta un Architecture Decision Record (ADR) para la decisión de usar WebSocket (Django Channels) en lugar de HTTP polling para el seguimiento GPS de repartidores en tiempo real en el sistema PicanteríaYa.

Contexto del sistema:
- Monolito modular en Django (ADR-001 ya decidido)
- Redis ya presente en la arquitectura como cola Celery
- Hasta 400 pedidos activos simultáneamente durante el pico dominical
- Equipo de 3 developers

Usa esta estructura:
# ADR-NNN: Título
- Estado: Aceptado
- Fecha: AAAA-MM-DD
- Decisores: ...
## Contexto
## Alternativas consideradas (al menos 3: polling, SSE, WebSocket)
## Decisión
## Consecuencias (positivas y negativas/riesgos)

Cita los IDs de drivers: RF-04 (seguimiento GPS), QA-01 (escalabilidad), R-02 (equipo), R-03 (presupuesto).
```

### Prompt 5 — Escenario de calidad QA-01 (entrada #5)

```
Ayúdame a redactar el escenario de atributo de calidad QA-01 de escalabilidad para el sistema PicanteríaYa, usando la plantilla de 6 partes de Bass, Clements y Kazman (2021).

Las 6 partes son: Fuente, Estímulo, Entorno, Artefacto, Respuesta, Medida.

Contexto:
- El pico de demanda es los domingos de 12:00 a 15:00 horas
- En ese horario los pedidos llegan a 400 por hora (×8 del flujo base de ~50/hora)
- La arquitectura tiene una cola Redis/Celery para absorber el pico
- La respuesta debe ser verificable con una métrica numérica con percentil estadístico

Completa la tabla de 6 partes con valores específicos y realistas para PicanteríaYa.
```
