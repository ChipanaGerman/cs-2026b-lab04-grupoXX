# E7: bitácora de uso de IA

24/11/2026, asistente Codex. Registro de interacciones reales de esta sesión; no se inventan turnos de estudiantes ni conversaciones con otros grupos.

| # | Entrada o situación | Propuesta del asistente | Verificación y corrección |
|---|---|---|---|
| 1 | Usuario solicita analizar guía, rúbrica y ejercicios antes de tocar Git | Inventariar archivos y leer las 21 páginas | Se localizaron ejercicio resuelto y rúbrica dentro de la guía; no archivos separados. Se presentó el plan sin modificar ni ejecutar Git. |
| 2 | Usuario: «comenza» | Rama codex/lab11-mcp y entorno aislado | Git detectó propietario diferente; se usó safe.directory solo por comando, sin cambiar la configuración global. Se conservaron cambios anteriores. |
| 3 | Diseño de Picantería Ya | Catálogo de menú, pedidos y reclamos | Se reutilizan Menu, Pedido, EstadoPedido y Decimal; se excluyen pagos y cambios de estado. E1 y E2 separados. |
| 4 | SDK 2 instalado | Inicialmente importar Context desde mcp.server | ImportError real; se corrigió a mcp.server.mcpserver.Context tras inspeccionar la API instalada. Sugerencia de código de IA corregida, no aceptada a ciegas. |
| 5 | Prueba del flujo MRTR | Esperar isError para tokens manipulados | El SDK devolvió error JSON-RPC -32602 invalid_request_state antes del handler. Se inspeccionó el resultado real y se corrigió la expectativa de esas dos pruebas; no se debilitó la seguridad para hacerlas pasar. |
| 6 | Usuario autoriza el reclamo ficticio exacto | Transmitir la confirmación al cliente interactivo | ModeloInteractivo, tools/call inicial input_required y continuación complete; UUID de reclamo en la traza. |
| 7 | Usuario indica VS Code con Copilot y que no tiene recursos ni catálogo ajeno | Configurar el host y recrear fixture educativa inerte | VS Code 1.98.2 no ofrece comandos MCP. Se documenta la limitación y no se finge un intercambio entre grupos. |
| 8 | npm resolvió Inspector obsoleto y Node instalado antiguo | Fijar Inspector 2.16.0 con Node 24 temporal | Conexión real MCP 2026-07-28; capturas del catálogo, menú válido y fecha inexistente. |
| 9 | Optimización de contexto | Acortar descripciones conservando contratos | Catálogo real pasa de 2513 a 2473 caracteres; estimación 629 a 619 tokens. Se informa que no es un tokenizer exacto. |
| 10 | Seguridad de terceros | Auditor por patrones y dos reglas nuevas | Catálogo propio sin alertas; fixture con siete hallazgos. Ninguna herramienta maliciosa fue invocada. |
| 11 | Host instalado incompatible | Usar copia oficial temporal VS Code 1.147.0 | Copilot consultó menú, cancelados y zonas mediante MCP. No se reemplazó la instalación 1.98.2. |
| 12 | La experiencia Copilot nueva no expone prompts/get | Usar la experiencia Local del editor para el prompt | La sugerencia /mcp.picanteria-ya.responder_reclamo recuperó la plantilla y produjo una respuesta real; capturas y transcripción guardadas. Se descartó la encuesta opcional sin enviar respuestas. |
| 13 | La escritura del host pide permiso | Detenerse y pedir autorización concreta para un segundo reclamo | El diálogo Allow tool permanece pendiente. No se reutiliza como segundo permiso la aprobación de E4 ni se registra un éxito inexistente. |
| 14 | Verificación final | Regresiones completas y exportación de commits | 143 pruebas locales y 29 contratos desde una exportación aislada en verde. Se preservan modificaciones anteriores fuera de los commits. |

La trayectoria de E4 contiene un error de fecha provocado intencionalmente y su corrección por el asistente al leer el mensaje de la herramienta. No se atribuye esa decisión a un modelo autónomo distinto.
