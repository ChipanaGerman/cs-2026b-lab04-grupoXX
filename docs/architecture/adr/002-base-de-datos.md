# ADR-002: Usar PostgreSQL como base de datos principal con esquemas separados por módulo

- Estado: Aceptado
- Fecha: 2026-09-30
- Decisores: Baca Calsin Leonardo Juan Jose, Chipana Jeronimo German Arturo, Mejia Rondan Giovanni Patrick

## Contexto

El sistema PicanteríaYa necesita persistir datos estructurados con relaciones claras entre entidades: clientes, picanterías, repartidores, pedidos, platos del menú y transacciones de pago. La arquitectura elegida (ADR-001) es un monolito modular con cinco módulos de dominio, por lo que la base de datos debe reflejar los límites entre módulos sin sacrificar la integridad referencial.

El atributo de calidad de rendimiento (QA-02, p95 ≤ 1 s en consulta de menú) y la escalabilidad ante el pico dominical (QA-01) exigen un motor de base de datos con soporte de indexación eficiente, transacciones ACID y compatibilidad con ORM (Django ORM). El presupuesto es bajo (R-03), por lo que la base de datos debe ejecutarse en el mismo VPS que la aplicación.

## Alternativas consideradas

1. **PostgreSQL relacional con esquemas separados por módulo** — Cada módulo (Menú, Pedidos, Pagos, Repartidores, Notificaciones) utiliza su propio esquema PostgreSQL (`menu`, `pedidos`, `pagos`, etc.) dentro de una sola instancia. Las claves foráneas cruzadas entre esquemas se permiten con prefijo explícito. Compatible con Django ORM nativamente. Elegida.

2. **MongoDB documental** — Esquema flexible; útil si los menús tienen estructuras variables por picantería. Sin embargo, no garantiza transacciones ACID multi-documento en todas las versiones, el equipo no tiene experiencia con Mongoose/MongoEngine en Django (R-02), y la consistencia de datos en el flujo de pedidos (pago → asignación → entrega) requiere transacciones confiables.

3. **SQLite** — Opción más simple, embebida, sin servidor separado. Descartada porque no soporta concurrencia de escritura simultánea: durante el pico de 400 pedidos/hora con workers Celery paralelos, SQLite genera bloqueos (locks) que harían fallar las transacciones (viola QA-01).

## Decisión

Usaremos **PostgreSQL 16** como única instancia de base de datos, ejecutada en el mismo VPS que la aplicación. Cada módulo de dominio tendrá su propio esquema PostgreSQL (`public.menu`, `public.pedidos`, `public.pagos`, `public.repartidores`, `public.notificaciones`). Las referencias cruzadas entre módulos se harán únicamente a través de la clave primaria (UUID), sin joins directos entre esquemas en la capa de aplicación — el módulo solicitante debe obtener los datos llamando al servicio del módulo propietario.

Adicionalmente, **Redis** se usará como caché de lectura para los menús del día (que cambian una vez al día por picantería), reduciendo la carga sobre PostgreSQL durante el pico dominical.

## Consecuencias

- **Positivas:**
  - Django ORM soporta PostgreSQL de forma nativa y madura; el equipo ya conoce esta combinación (R-02).
  - Los esquemas separados refuerzan los límites entre módulos y facilitan una futura migración a bases de datos independientes si se adoptan microservicios.
  - Las transacciones ACID garantizan que un pedido no quede en estado inconsistente si falla el pago o la asignación del repartidor.
  - La caché Redis para menús reduce la carga de lectura en el pico dominical (mejora QA-01 y QA-02).

- **Negativas / riesgos:**
  - La instancia única de PostgreSQL es un punto único de falla para todos los módulos; se mitiga con backups automáticos diarios (pg_dump) y monitoreo de salud.
  - Si en el futuro se decide extraer un módulo como microservicio independiente, su esquema deberá migrarse a una instancia separada, lo que implica trabajo de migración de datos.
  - El crecimiento descontrolado de la tabla de pedidos puede degradar las consultas; se programan índices en `pedido.estado`, `pedido.picanteria_id` y `pedido.created_at` desde el inicio.
