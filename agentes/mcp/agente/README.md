# E4: agente del Lab 10 vía MCP

Ejecutar desde la raíz con `.venv-mcp/Scripts/python -X utf8 -B -m agentes.mcp.agente.ejecutar`.
Se reutilizan sin cambios `Agente`, `ModeloInteractivo` y el validador de decisiones del Lab 10. El adaptador descubre el catálogo; no replica consultas de negocio. La política solo permite tres herramientas y el adaptador tramita la confirmación MRTR de escritura.

## Ejecución real del 24/11/2026

Consulta: menú de La Tradición, pedidos cancelados y registro de reclamo sujeto a permiso. Las decisiones JSON fueron pegadas por el asistente después de observar cada resultado, usando ModeloInteractivo, no ModeloGrabado.

1. `menu_del_dia` con `24/11/2026`: error de negocio `isError=true`; la herramienta explica AAAA-MM-DD.
2. El asistente corrige a `2026-11-24`: rocoto S/25.00 y chupe S/35.50.
3. `pedidos_por_estado(CANCELADO)`: pedido 00000000-0000-0000-0000-000000000001, S/25.00.
4. `registrar_reclamo`: resultado `input_required`; no se ha escrito todavía.
5. El usuario autorizó explícitamente en el chat la creación para ese pedido y el texto «Pedido cancelado sin explicación; solicito revisión.». Se transmitió esa respuesta como `s` a la consola. No fue una aprobación autónoma del asistente.
6. Continuación con `requestState` e `inputResponses`: `creado=true`, reclamo e73a1d0d-e009-4f04-9fb5-cb5d4185c8e2.

Evidencias: `../trayectorias/consulta-negocio.json` (decisiones literales), `../trayectorias/aprobacion.json`, `../trazas/agente-negocio.jsonl` (máquina de estados) y `../trazas/negocio.jsonl` (tráfico real). Los tokens opacos de la traza pertenecen a un subproceso terminado y no son credenciales persistentes.

La aprobación aparece en el registro del adaptador y en MRTR; el núcleo antiguo solo tiene un estado específico para editar_archivo y por eso su campo genérico `aprobacion` dice «no aplica» para MCP. No debe interpretarse como ausencia de aprobación.
