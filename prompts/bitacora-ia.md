# Bitácora de IA · Laboratorio 9

| Interacción con Codex | Revisión y decisión | Evidencia |
| --- | --- | --- |
| Lectura de la guía y desglose de E1–E8 | Incorporar los requisitos de grabaciones, revisión cruzada y reto | README del laboratorio |
| Inventario de historias | Rechazar la propuesta de tratar las historias reconstruidas como seis historias de Jira. Solo HU-01 consta como historia formal en el repositorio | `docs/design/historia.md` y metadatos de `criterios/casos.yaml` |
| Diseño de criterios automáticos | Acotar las palabras técnicas a los escenarios. H7 podría citar Redis en una pregunta válida al PO | `criterios/aserciones.py`, caso H7 |
| Adaptación del contrato de commits | Usar un esquema de cadena para conservar el encabezado sin comillas JSON | `commits/esquema.json` y pruebas del generador |
| Integración con el puerto de IA | Mantener `ProveedorLLM` y rechazar respuestas inválidas con pruebas deterministas | `src/pedidos/generador_prompts.py` y `tests/test_generadores_prompts.py` |
| Plan del reto | Comparar dos modelos locales con idénticos casos y medir latencia por caso | `reto/README.md` |

## No determinismo

Se intentaron las nueve llamadas con ERNIE 5.5 Flash Preview. Kilo devolvió HTTP 429 `PROMOTION_MODEL_LIMIT_REACHED` y las llamadas no entregaron texto para comparar. Las capturas previas de v3.1 aportan una observación por caso, pero siguen faltando las tres rondas independientes.

Usar la v3.1 sobre H1, H7 y H8 en tres conversaciones nuevas por caso, con el mismo modelo y configuración. Guardar las nueve salidas en `criterios/repeticiones/<ronda>/<id>.txt` y registrar modelo, fecha y parámetros. Comparar formato, decisión INVEST, escenarios o preguntas, y fidelidad. Registrar en cinco líneas qué varió entre rondas y si esa variación cambió la calificación. La observación experimental está pendiente.
