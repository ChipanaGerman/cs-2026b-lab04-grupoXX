# Reto B: confirmación mediante MRTR

Implementado con el SDK oficial 2.3.0 y protocolo 2026-07-28. No se simula `input_required` dentro de un campo de texto: es el resultado discriminado de `tools/call`.

Flujo: solicitud de registrar_reclamo → `resultType: input_required`, `inputRequests.confirmar` (`elicitation/create`, formulario booleano) y `requestState` → cliente presenta pedido y descripción → humano confirma → se repite tools/call con mismos argumentos, requestState e inputResponses → resultado `complete` y structuredContent con el UUID creado.

El SDK autentica requestState y lo vincula a los argumentos; el servidor añade vencimiento de cinco minutos, límite de 100 pendientes y consumo único del token. Cancelación, rechazo y respuesta sin booleano true no crean archivos. Un reinicio invalida confirmaciones pendientes; hay que empezar de nuevo. Esto es deliberado en el prototipo stdio, no una solución distribuida.

Prueba automatizada (sin humano, datos temporales): `.venv-mcp/Scripts/python -B -m pytest -q agentes/mcp/pruebas/test_mrtr.py`.

Prueba con aprobación humana real: ejecución E4 documentada en `../agente/README.md` y traza `../trazas/negocio.jsonl`. Las respuestas de aceptación usadas por pytest son fixtures de prueba; no se presentan como permisos humanos.
