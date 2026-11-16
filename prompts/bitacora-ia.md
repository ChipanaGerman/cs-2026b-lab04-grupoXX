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

Se usó la v3.1 con GPT-6 Luna en modo Rápido de Duck.ai, en nueve chats nuevos, después de que Kilo agotara su cuota anónima. Los textos y los metadatos están en [repeticiones](criterios/repeticiones/).

1. H1 conservó éxito y rechazo en las tres rondas. Cambiaron los títulos, la persona gramatical y el momento descrito en el Dado.
2. H7 fue no INVEST en las tres rondas. Las preguntas variaron entre resultado observable, alcance funcional y verificación.
3. H8 conservó el filtro y el aviso sin resultados. El marcador quedó fuera de las tres respuestas.
4. H8 usó a Yape como actor en dos rondas y redactó el filtro en primera persona en la tercera. Las aserciones no detectaron esa diferencia.
5. Las nueve respuestas pasaron las seis aserciones. Las grabaciones permiten repetir el resultado de esas aserciones y las nuevas llamadas muestran variaciones de contenido.
