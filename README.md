# PicanteríaYa — Laboratorio 04: Fundamentos de arquitectura de software

Construcción de Software · EPIS-UNSA · 2026-B · Grupo XX

---

## Integrantes

| Nombre | Rol en el laboratorio |
|--------|-----------------------|
| Baca Calsin Leonardo Juan Jose | Redactor de drivers y escenarios de calidad (E1), revisión de ADR |
| Chipana Jeronimo German Arturo | Diagramador (E3, E5, E6), configuración del repositorio |
| Mejia Rondan Giovanni Patrick | Redactor de ADR (E4), bitácora de IA (E7) |

---

## Caso

**PicanteríaYa** es una plataforma de delivery de picanterías arequipeñas que conecta a clientes, picanterías y repartidores. Los clientes consultan el menú del día de cada picantería, realizan pedidos y pagan con Yape; el sistema asigna automáticamente un repartidor disponible y el cliente puede seguir la ubicación del repartidor en tiempo real en el mapa.

El **atributo de calidad crítico** es la **escalabilidad**: los domingos de 12:00 a 15:00 los pedidos se multiplican por 8 respecto al flujo base (~50 pedidos/hora), alcanzando hasta **400 pedidos/hora**. La arquitectura debe absorber este pico sin rechazar pedidos ni degradar la experiencia del usuario (p95 del tiempo de confirmación ≤ 4 s, 0 pedidos rechazados por sobrecarga).

---

## Arquitectura elegida

**Estilo: Monolito Modular + Cola de mensajes Redis/Celery**  
Puntaje en matriz de decisión: **4,20 / 5,00** (ver [matriz-decision.md](docs/architecture/matriz-decision.md))

```mermaid
flowchart TB
    CL["🧑‍💻 Cliente\n(app web / PWA)"]
    PI["🍲 Picantería\n(panel web)"]
    RE["🛵 Repartidor\n(app móvil)"]

    subgraph APP["PicanteríaYa — Monolito Modular (un solo despliegue en VPS)"]
        API["Capa de Presentación\nAPI REST (Django REST Framework)\nWebSocket (Django Channels)"]

        subgraph MODULOS["Módulos de Dominio"]
            M1["📋 Menú\ny Catálogo"]
            M2["📦 Pedidos"]
            M3["💳 Pagos"]
            M4["🛵 Repartidores\ny GPS"]
            M5["🔔 Notificaciones"]
        end

        INF["Capa de Infraestructura\n(repositorios, adaptadores externos)"]
        COLA["🔴 Cola Redis\n+ Workers Celery\n(procesamiento asíncrono)"]
    end

    DB[("🐘 PostgreSQL\n(esquema por módulo)")]
    CACHE[("⚡ Redis\n(caché de menús)")]
    CULQI["💰 Culqi / Niubiz\n(pasarela Yape)"]
    GMAPS["🗺️ Google Maps API\n(seguimiento GPS)"]
    NOTIF["📱 FCM / WhatsApp API\n(notificaciones push)"]

    CL & PI & RE --> API
    API --> M1 & M2 & M3 & M4 & M5
    M2 --> COLA
    COLA --> M3 & M4 & M5
    M1 & M2 & M3 & M4 & M5 --> INF
    INF --> DB
    INF --> CACHE
    INF --> CULQI
    INF --> GMAPS
    INF --> NOTIF

    classDef mod fill:#FFF3E0,stroke:#E65100,color:#000
    classDef ext fill:#F3E5F5,stroke:#6A1B9A,color:#000,stroke-dasharray: 4 3
    classDef usr fill:#E3F2FD,stroke:#1565C0,color:#000
    classDef infra fill:#E8F5E9,stroke:#2E7D32,color:#000
    classDef cola fill:#FFEBEE,stroke:#C62828,color:#000

    class M1,M2,M3,M4,M5 mod
    class CULQI,GMAPS,NOTIF ext
    class CL,PI,RE usr
    class INF,DB,CACHE infra
    class COLA cola
```

---

## Decisiones arquitectónicas

- [ADR-001: Estilo arquitectónico — Monolito modular con cola de mensajes](docs/architecture/adr/001-estilo-arquitectonico.md)
- [ADR-002: Base de datos — PostgreSQL con esquemas separados por módulo](docs/architecture/adr/002-base-de-datos.md)
- [ADR-003: Comunicación en tiempo real — WebSocket con Django Channels](docs/architecture/adr/003-comunicacion-tiempo-real.md)

---

## Estructura del repositorio

```
cs-2026b-lab04-grupoXX/
├── README.md
└── docs/
    └── architecture/
        ├── drivers.md               # E1: drivers y escenarios de calidad
        ├── matriz-decision.md       # E2: alternativas y decisión ponderada
        ├── bitacora-ia.md           # E7: 5+ interacciones con IA verificadas
        └── diagramas/
            ├── arquitectura.mmd     # E3: Mermaid — arquitectura elegida
            ├── alternativa.puml     # E5: PlantUML — alternativa descartada
            ├── despliegue.py        # E6: Python Diagrams — vista de despliegue
            └── img/                 # Imágenes exportadas (PNG/SVG)
        └── adr/
            ├── 000-plantilla.md
            ├── 001-estilo-arquitectonico.md
            ├── 002-base-de-datos.md
            └── 003-comunicacion-tiempo-real.md
```

---

## Reflexión sobre el uso de la IA

El uso de asistentes de IA en este laboratorio aceleró significativamente las primeras etapas del diseño: en minutos obtuvimos tres alternativas arquitectónicas con sus pros y contras, y borradores de ADR bien estructurados. Sin embargo, la IA demostró limitaciones importantes que obligaron al equipo a ejercer juicio crítico.

El error más revelador fue que Claude asumió que **Yape dispone de una API pública abierta** para integración directa, lo cual es incorrecto: verificamos en la documentación oficial de Yape y en foros de desarrollo peruano que la integración requiere un proveedor intermediario con acuerdo comercial. Este error habría impactado directamente el MVP si lo hubiéramos aceptado sin verificar.

También notamos que la IA tiende a **proponer arquitecturas sobredimensionadas**: recomendó Kubernetes y microservicios para 400 pedidos/hora, cuando calculamos que equivale a 6–7 pedidos/minuto, perfectamente manejables con un monolito y una cola asíncrona. La IA no ponderó nuestras restricciones de equipo (3 developers sin DevOps) ni de presupuesto (VPS único de $20/mes).

El aprendizaje central: **la IA es un excelente generador de borradores y listas de opciones**, pero no conoce el contexto real del proyecto ni las restricciones del equipo. Cada propuesta debe verificarse contra la documentación oficial y los drivers del sistema.

---

## Recursos y herramientas

- Editor Mermaid en línea: https://mermaid.live
- Editor PlantUML en línea: https://www.plantuml.com/plantuml
- Python Diagrams: https://diagrams.mingrammer.com/
- Guía de la práctica: `Guia_Lab04_Fundamentos_Arquitectura_Software_2026B.pdf`
