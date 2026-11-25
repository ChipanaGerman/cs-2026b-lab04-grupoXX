# ADR-011: exposición de Picantería Ya mediante MCP

- Fecha: 2026-11-24
- Estado: aceptado para prototipo educativo local
- Contexto: Labs 09 y 10 ya definen prompts y un agente con herramientas locales. El equipo necesita consultar menú y pedidos desde hosts distintos y registrar reclamos con permiso sin duplicar la lógica por cada asistente.

## Decisión

Publicar un servidor MCP con el SDK oficial Python mcp 2.3.0 y transporte stdio. Usar protocolo 2026-07-28: server/discover, versión y capacidades por petición, sin initialize; confirmar la creación de reclamos mediante MRTR input_required y continuación explícita.

Exponer menu_del_dia y pedidos_por_estado como consultas parametrizadas con salida Pydantic; registrar_reclamo como la única escritura, limitada a crear registros ficticios nuevos. Publicar cobertura y reglas como recursos, ADR por URI plantilla y responder_reclamo como prompt del equipo. La capa MCP delega en src/pedidos/consultas_mcp.py, que utiliza las entidades, estados, disponibilidad de platos y cálculo de total del dominio.

No exponer cobros Yape, datos personales de clientes, seguimiento GPS real, SQL libre, shell, edición de código, cancelación de pedidos ni borrado de reclamos. Este laboratorio no convierte los adaptadores externos incompletos del proyecto en servicios productivos.

## Controles

Validar fechas, longitud, enum de estado y UUID existente; limitar consultas a 20 pedidos. Mantener Decimal y serializar dinero como texto. Resolver ADR solo dentro de su carpeta y rechazar rutas no numéricas. La única creación usa carpeta configurada por el operador, UUID generado y apertura exclusiva. La confirmación está vinculada a los argumentos por el SDK y a un token temporal de un solo uso por la aplicación. El cliente debe obtener consentimiento humano real; el servidor no puede probar quién presionó aceptar.

Fijar dependencias, auditar catálogos ajenos, tratar texto externo como datos y no dar secretos al proceso. No conectar la fixture maliciosa a un LLM. Anotaciones declarativas complementan las restricciones, no las reemplazan. Mantener stdout exclusivo para JSON-RPC y diagnósticos en stderr.

## Alternativas descartadas

| Alternativa | Ventaja | Motivo de descarte para este laboratorio |
|---|---|---|
| API REST directa por host | Familiar, control HTTP explícito | Cada host necesita adaptar descubrimiento, esquemas, recursos, prompts y consentimiento. Puede coexistir para aplicaciones no MCP. |
| Function calling dentro del agente | Sencillo para un solo agente | Duplica integración y permisos al conectar Copilot y otros modelos; acopla herramientas al host. |
| Streamable HTTP | Compartir capacidades entre equipos | No necesario para Reto B; exige autenticación/autorización, cuotas y estado de confirmación compartido. |
| Herramienta genérica ejecutar_comando | Flexibilidad | Privilegios excesivos, ejecución arbitraria y contratos poco verificables. |

## Consecuencias y evidencia

Positivas: catálogo pequeño, reutilización con el Lab 10, contratos offline, tráfico auditable y confirmación antes de crear. Costos: arranque del subproceso, catálogo en contexto y dependencia de compatibilidad del host. El prototipo guarda pendientes en memoria: un reinicio exige repetir la confirmación y no se ofrece durabilidad distribuida.

Evidencias en agentes/mcp/: Inspector, pruebas, trayectoria, traza, métricas y auditoría. E6 midió 14 mensajes y 8327 bytes; catálogo optimizado de 629 a 619 tokens estimados. La evidencia del host debe revisarse en uso-en-host.md: disponer de configuración no demuestra que Copilot la haya utilizado.

## Fuentes primarias

- [Especificación MCP 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28)
- [SDK oficial Python](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Inspector oficial](https://github.com/modelcontextprotocol/inspector)

La guía docente y su rúbrica se encuentran en Guia_Lab11_Protocolos_MCP_2026B.pdf, pp. 15–21. No se publica esa guía como código del proyecto.
