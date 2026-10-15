# Inventario de elementos C4 — PicanteríaYa

> **E1 — Lab 06** | Fuente única: todos los elementos provienen de artefactos ya construidos en los Labs 04 y 05.

---

## Tabla de elementos del modelo

| Elemento | Tipo C4 | Descripción breve | Origen (artefacto) |
|----------|---------|-------------------|--------------------|
| **Cliente** | Persona | Persona que consulta el menú del día, realiza pedidos y paga con Yape | `drivers.md` (RF-01, RF-02) |
| **Picantería** | Persona | Negocio que publica su menú diario y atiende los pedidos asignados | `drivers.md` (RF-05) |
| **Repartidor** | Persona | Persona que recibe la asignación, recoge el pedido y lo entrega | `drivers.md` (RF-06) |
| **PicanteríaYa** | Sistema de software | Plataforma de delivery de picanterías arequipeñas: menú, pedidos, pagos y seguimiento en tiempo real | Caso del Lab 04 |
| **Culqi (pasarela de pagos)** | Sistema externo | Proveedor intermediario que procesa cobros con Yape | `drivers.md` (R-05), `ADR-001` |
| **Google Maps API** | Sistema externo | API de mapas para mostrar la ubicación del repartidor en tiempo real | `drivers.md` (R-06) |
| **WhatsApp / FCM** | Sistema externo | Servicio de notificaciones push y mensajería al cliente y picantería | `drivers.md` (RF-07) |
| **App Cliente / PWA** | Contenedor | Interfaz web progresiva usada por el cliente para ver menú, pedir y pagar | `ADR-001`, `despliegue.py` (Lab 04) |
| **App Repartidor** | Contenedor | Aplicación móvil del repartidor para recibir asignaciones y actualizar su posición GPS | `drivers.md` (RF-06), `ADR-001` |
| **API PicanteríaYa** | Contenedor | Monolito modular Django REST Framework que implementa todos los casos de uso | `ADR-001` |
| **Worker de tareas (Celery)** | Contenedor | Ejecuta de forma asíncrona la asignación de repartidores, notificaciones y reintentos de pago | `ADR-001` |
| **Base de datos (PostgreSQL)** | Contenedor | Almacena clientes, picanterías, menús, pedidos, pagos y repartidores (esquema por módulo) | `ADR-002`, `despliegue.py` |
| **Cola y caché (Redis)** | Contenedor | Cola de tareas Celery y caché de menús del día para reducir consultas en pico dominical | `ADR-001`, `despliegue.py` |
| **Servicio GPS / WebSocket** | Contenedor | Canal WebSocket (Django Channels) para el seguimiento en tiempo real del repartidor | `ADR-003`, `despliegue.py` |
| **Módulo Menú** | Componente (de la API) | Publica y actualiza el menú diario de cada picantería con su stock | `paquetes.puml` (Lab 05) |
| **Módulo Pedidos** | Componente (de la API) | Gestiona el carrito, la confirmación y el ciclo de vida del pedido | `paquetes.puml`, `clases.puml` (Lab 05) |
| **Módulo Pagos** | Componente (de la API) | Procesa el cobro con Yape vía el puerto PasarelaPago → Culqi | `paquetes.puml`, `clases.puml` (Lab 05) |
| **Módulo Repartidores** | Componente (de la API) | Asigna el repartidor más cercano disponible (encola tarea en Celery) | `paquetes.puml`, `actividades-asignacion-repartidor.puml` (Lab 05) |
| **Módulo Notificaciones** | Componente (de la API) | Envía notificaciones push/SMS al cliente y a la picantería | `paquetes.puml` (Lab 05) |
| **Flujo "Pedir menú y pagar con Yape"** | Vista dinámica | Flujo completo: cliente selecciona platos, paga con Yape, se asigna repartidor | `secuencia-pedir-pagar.puml` (Lab 05) |
| **Entorno Producción (VPS)** | Vista de despliegue | VPS Ubuntu 24.04 (2 vCPU, 4 GB RAM, ~$20/mes) con Docker Compose | `drivers.md` (R-03), `despliegue.py` (Lab 04) |

---

## Notas de verificación

- **Culqi como sistema externo** (no contenedor): PicanteríaYa no construye ni despliega la pasarela de pagos → correcto según ADR-001 (R-05).
- **Google Maps API como sistema externo**: se usa solo lectura con control de costos (R-06); no se despliega como contenedor propio.
- **Docker Compose no es un contenedor C4**: es infraestructura de despliegue; aparece como nodo en la vista de despliegue.
- **App Repartidor** es un contenedor separado porque tiene ciclo de vida de despliegue independiente (app móvil) respecto a la PWA del cliente.
