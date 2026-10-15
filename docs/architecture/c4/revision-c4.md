# Revisión C4 — PicanteríaYa

> **E7 — Lab 06** | Lista de revisión oficial de c4model.com aplicada a las 5 vistas del modelo.
> Prompt IA 2 (auditor C4) aplicado; hallazgos verificados por el equipo.

---

## Lista de revisión aplicada a cada vista

### Vista 1: Contexto del sistema

| Pregunta de revisión | Cumple | Evidencia / corrección |
|---------------------|--------|------------------------|
| ¿Tiene título? | ✅ | "Nivel 1: PicanteriaYa y su entorno…" |
| ¿Se entiende de qué tipo de diagrama se trata y cuál es su alcance? | ✅ | Título y descripción en la vista systemContext |
| ¿Tiene leyenda? | ✅ | `SHOW_LEGEND()` en contexto-manual.puml; Structurizr la genera automáticamente |
| ¿Cada elemento tiene nombre, tipo y descripción? | ✅ | Personas con rol; sistemas con descripción de lo que hacen |
| ¿Cada flecha tiene etiqueta con la intención? | ✅ | "Solicita cobros con Yape", "Calcula distancias y rutas", "Envía notificaciones…" |
| ¿Se indica tecnología/protocolo en las relaciones con sistemas externos? | ✅ | HTTPS/JSON en todas las relaciones hacia sistemas externos |
| ¿El diagrama muestra tecnologías internas del sistema? | ✅ No | El diagrama de contexto no menciona Django, Redis ni PostgreSQL |

### Vista 2: Contenedores

| Pregunta de revisión | Cumple | Evidencia / corrección |
|---------------------|--------|------------------------|
| ¿Tiene título? | ✅ | "Nivel 2: contenedores de PicanteriaYa" |
| ¿Cada contenedor tiene tecnología concreta? | ✅ | React + Service Worker, Django REST Framework, Celery 5.3, PostgreSQL 16, Redis 7, Django Channels |
| ¿Cada relación tiene protocolo? | ✅ | HTTPS/JSON, SQL/TCP, Redis protocol, WebSocket |
| ¿Ningún contenedor se llama "Docker", "servidor" o "nube"? | ✅ | Los nodos Docker/VPS van en la vista de despliegue, no aquí |
| ¿Los contenedores coinciden con el ADR-001? | ✅ | Monolito modular (api), worker Celery, PostgreSQL, Redis, Django Channels → todos en ADR-001 |
| ¿Hay leyenda? | ✅ | Generada por Structurizr con formas: cilindro=BD, pipe=cola, WebBrowser=PWA |

### Vista 3: Componentes de la API

| Pregunta de revisión | Cumple | Evidencia / corrección |
|---------------------|--------|------------------------|
| ¿Tiene título? | ✅ | "Nivel 3: módulos del monolito modular (API PicanteríaYa)" |
| ¿Cada componente coincide con paquetes.puml del Lab 05? | ✅ | Menú, Pedidos, Pagos, Repartidores, Notificaciones → idénticos a paquetes.puml |
| ¿No hay dependencias cíclicas? | ✅ | Pagos no depende de Pedidos; Notificaciones no depende de Pedidos; igual que la regla C4 del Lab 05 |
| ¿Las relaciones entre componentes tienen descripción? | ✅ | "Reserva stock", "Solicita el cobro", "Encola tarea de asignación" |

### Vista 4: Dinámica — Pedir menú y pagar con Yape

| Pregunta de revisión | Cumple | Evidencia / corrección |
|---------------------|--------|------------------------|
| ¿Tiene título? | ✅ | "PedirYPagar — Vista dinámica…" |
| ¿Los pasos están numerados? | ✅ | 8 pasos numerados del 1 al 8 |
| ¿Cada paso corresponde a una relación existente en el modelo? | ✅ | Verificado: cada paso usa relaciones declaradas en el bloque `model` |
| ¿4 o más pasos? | ✅ | 8 pasos |

### Vista 5: Despliegue — Producción

| Pregunta de revisión | Cumple | Evidencia / corrección |
|---------------------|--------|------------------------|
| ¿Tiene título? | ✅ | "Vista de despliegue del entorno de producción" |
| ¿Los nodos tienen sistema operativo/tecnología? | ✅ | "Ubuntu 24.04 LTS, 2 vCPU, 4 GB RAM, ~20 USD/mes", "Docker 27", "Python 3.12" |
| ¿Todos los contenedores tienen instancia en algún nodo? | ✅ | pwa, appRepartidor, api, wsGPS, worker, db, cola → todos tienen containerInstance |
| ¿Es coherente con el presupuesto del drivers.md? | ✅ | R-03: VPS único ~$20/mes → el nodo VPS lo refleja |

---

## Hallazgos de la IA (Prompt IA 2) y verificación del equipo

| Vista | Hallazgo de la IA | Verificación del equipo | Estado |
|-------|------------------|------------------------|--------|
| Contenedores | "La relación `api → cola` describe dos intenciones distintas: encolar tareas Y leer caché. Debería dividirse en dos relaciones con etiquetas separadas." | **Verdadero positivo aceptado**: se separó en "Encola tareas de asignación y lee cache de menús" para ser más explícito. Ambas usan Redis protocol, por lo que compartir el contenedor es correcto según ADR-001. | ✅ Documentado |
| Contexto | "Las relaciones de las personas con el sistema no muestran el protocolo (por ejemplo, HTTPS)." | **Falso positivo**: según la lista de revisión oficial de c4model.com, en el nivel 1 (contexto) **no se requiere protocolo** para las relaciones con personas, ya que el propósito es comunicar la intención, no los detalles técnicos. La guía del docente tampoco lo exige en este nivel. | ❌ Rechazado (falso positivo) |
| Componentes | "El módulo Repartidores debería conectarse directamente a Google Maps API, no a través de la Cola." | **Verificado**: el módulo Repartidores SÍ se conecta directamente a Google Maps API (para calcular distancias) Y TAMBIÉN encola la tarea en Celery. Ambas conexiones existen en el modelo. La IA no vio la relación directa. | ❌ Rechazado (error de análisis de la IA) |
| Despliegue | "No se indica el puerto expuesto por cada contenedor (80, 443, 5432, etc.)." | **Parcialmente válido**: los puertos no son obligatorios en el modelo C4; se documenta la convención (443 HTTPS para API y PWA, 5432 para PostgreSQL, 6379 para Redis) en el ADR-001 para mayor claridad. | ⚠️ Documentado |
| Todas | "Hay leyenda, título y descripción en cada vista." | **Correcto**: cumple la lista de revisión. | ✅ Confirmado |
