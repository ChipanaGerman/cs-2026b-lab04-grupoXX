# ADR-003: Comunicación en tiempo real con repartidores mediante WebSocket (Django Channels)

- Estado: Aceptado
- Fecha: 2026-09-30
- Decisores: Baca Calsin Leonardo Juan Jose, Chipana Jeronimo German Arturo, Mejia Rondan Giovanni Patrick

## Contexto

Uno de los requisitos funcionales clave del MVP es que el cliente pueda realizar el **seguimiento en tiempo real de la ubicación del repartidor en el mapa** (RF-04). Esto implica que el servidor debe recibir actualizaciones de posición GPS desde la app del repartidor y retransmitirlas al cliente prácticamente sin latencia perceptible.

El atributo de escalabilidad (QA-01) añade presión: durante el pico dominical pueden existir hasta 400 pedidos activos simultáneamente, lo que significa hasta 400 conexiones concurrentes de seguimiento en tiempo real. Cualquier solución basada en HTTP polling genera 400 requests/s adicionales al servidor, saturándolo.

La arquitectura elegida (ADR-001) ya incluye Redis como broker de Celery; reutilizarlo como backend de Channel Layers para Django Channels no añade infraestructura nueva.

## Alternativas consideradas

1. **HTTP Polling desde el cliente** — El cliente (app web) realiza una petición HTTP cada 5 segundos para obtener la posición del repartidor. Fácil de implementar, pero genera una carga de 400 pedidos × 12 req/min = 4 800 requests/minuto adicionales durante el pico; ineficiente y costoso en ancho de banda. Viola QA-01.

2. **Server-Sent Events (SSE)** — El servidor envía actualizaciones al cliente a través de una conexión HTTP unidireccional permanente. Compatible con todos los navegadores modernos, no requiere WebSocket. Sin embargo, la comunicación es unidireccional (servidor → cliente únicamente), lo que dificulta enviar confirmaciones de recepción o controles de sesión desde el cliente.

3. **WebSocket con Django Channels y Redis Channel Layer** — Conexión bidireccional persistente entre el cliente y el servidor. El repartidor publica su posición vía WebSocket; el servidor la retransmite al cliente suscrito al mismo pedido a través del Channel Layer en Redis. Aprovecha la infraestructura Redis ya existente (ADR-001). Elegida.

## Decisión

Usaremos **Django Channels** con el protocolo **WebSocket** para la comunicación en tiempo real entre la app del repartidor y la app del cliente. El backend de Channel Layers será **Redis** (el mismo servidor Redis usado para la cola Celery), configurado con `channels_redis`.

El flujo de datos será:
1. La app del repartidor envía su posición GPS cada 5 segundos vía WebSocket al endpoint `/ws/pedido/{pedido_id}/gps/`.
2. El Consumer de Django Channels publica la posición en el grupo de canales `pedido_{pedido_id}`.
3. La app del cliente, conectada al mismo grupo, recibe la posición en tiempo real y actualiza el marcador en Google Maps.

Para el MVP, si Django Channels no puede instalarse por restricciones del servidor, se usará **polling cada 10 s** como fallback, documentándolo en el README.

## Consecuencias

- **Positivas:**
  - Elimina el overhead de 4 800 requests/min que generaría el polling durante el pico dominical; reduce la carga del servidor en ~80 % comparado con polling cada 5 s (mejora QA-01 y QA-02).
  - Reutiliza Redis ya presente en la arquitectura, sin añadir nueva infraestructura (coherente con R-03).
  - La experiencia de usuario mejora notablemente: actualizaciones en tiempo real vs. actualizaciones cada 5–10 s con polling.

- **Negativas / riesgos:**
  - Django Channels añade complejidad al despliegue: requiere `daphne` o `uvicorn` como servidor ASGI en lugar del WSGI clásico (`gunicorn`); el equipo debe aprender esta diferencia (R-02).
  - Si Redis cae, las conexiones WebSocket activas se pierden; se mitiga con un cliente que reconecta automáticamente (exponential backoff) y el fallback a polling.
  - En el VPS de un solo core, el número de conexiones WebSocket concurrentes puede ser un límite; se monitorea con Grafana y se evalúa aumentar workers si supera 200 conexiones simultáneas.
