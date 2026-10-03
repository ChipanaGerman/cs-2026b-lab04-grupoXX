# ADR-001: Adoptar un monolito modular con cola de mensajes para el MVP de PicanteríaYa

- Estado: Aceptado
- Fecha: 2026-09-29
- Decisores: Baca Calsin Leonardo Juan Jose, Chipana Jeronimo German Arturo, Mejia Rondan Giovanni Patrick

## Contexto

El sistema PicanteríaYa debe atender a tres actores (Cliente, Picantería, Repartidor) con un MVP listo en 1 mes (R-01), desarrollado por 3 developers con experiencia en Python/Django pero sin experiencia en DevOps avanzado (R-02), sobre un único VPS de bajo costo (R-03).

El atributo de calidad crítico es la **escalabilidad** (QA-01): los domingos de 12:00 a 15:00, los pedidos se multiplican por 8 respecto al flujo base (~50 pedidos/hora), alcanzando hasta 400 pedidos/hora. La arquitectura debe absorber este pico sin rechazar pedidos ni degradar la experiencia del usuario.

Adicionalmente, la integración con Yape no dispone de API pública (R-05), por lo que los pagos deben canalizarse a través de un proveedor intermediario como Culqi o Niubiz.

## Alternativas consideradas

1. **Monolito en capas (n-tier)** — puntaje matriz: 3,65. Simple y rápido de construir, pero no ofrece mecanismos nativos para absorber picos de carga; el escalado implica replicar todo el proceso.
2. **Monolito modular + cola Redis/Celery** — puntaje matriz: **4,20**. Un solo despliegue con módulos de dominio bien delimitados. La cola asíncrona absorbe el pico de pedidos sin bloquear la API. Elegido.
3. **Microservicios** — puntaje matriz: 3,25. Escalabilidad fina, pero requiere API Gateway, orquestación, monitoreo distribuido y múltiples bases de datos; excede la capacidad operativa del equipo en 1 mes.

## Decisión

Usaremos un **monolito modular con Django REST Framework**, dividido en cinco módulos de dominio: **Menú**, **Pedidos**, **Pagos**, **Repartidores/GPS** y **Notificaciones**. Cada módulo se comunica únicamente a través de interfaces públicas (servicios de aplicación) y comparte una única instancia de PostgreSQL con esquemas separados por módulo.

Las operaciones costosas durante el pico dominical (asignación de repartidor, procesamiento de pago, envío de notificaciones) se gestionan de forma **asíncrona mediante una cola Redis y workers Celery**, de modo que la API responde inmediatamente al cliente con un `pedido_recibido` y el procesamiento pesado se ejecuta en segundo plano.

El módulo de Repartidores/GPS usa **Django Channels (WebSocket)** para el seguimiento en tiempo real sin necesidad de polling. La caché Redis también almacena los menús del día para reducir consultas a la base de datos durante el pico.

## Consecuencias

- **Positivas:**
  - Un único despliegue en el VPS reduce el costo operativo y la complejidad de CI/CD (coherente con R-03).
  - La cola Redis/Celery permite absorber el pico dominical de ×8 sin rechazar pedidos (resuelve QA-01).
  - Los módulos con interfaces explícitas pueden extraerse como microservicios en el futuro si la carga crece sostenidamente por encima de los 400 pedidos/hora.
  - El equipo puede construir y operar el sistema dentro del plazo de 1 mes (R-01, R-02).

- **Negativas / riesgos:**
  - Una falla crítica en el proceso principal afecta a todos los módulos simultáneamente (punto único de falla); se mitiga con Supervisor/systemd para reinicio automático y un health-check periódico (QA-03: recuperación ≤ 30 s).
  - El equipo debe respetar estrictamente los límites entre módulos (sin imports cruzados directos); se usará `import-linter` en la integración continua para forzar esta restricción.
  - Si la demanda crece significativamente más allá del pico actual, el monolito puede convertirse en un cuello de botella; en ese punto la migración a microservicios será el siguiente paso arquitectónico.
