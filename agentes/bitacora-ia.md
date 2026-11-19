# E7. Bitácora de interacciones con Codex

Fecha: 19/11/2026. Asistente: Codex de esta sesión. No se afirma intervención
de otros modelos ni de integrantes que no participaron. Los JSON exactos
están en trayectorias/; observaciones completas, en trazas/.

| N.º | Entrada/objetivo | Respuesta y acción | Verificación / decisión |
|---|---|---|---|
| 1 | Guía y rúbrica: aplicar PicanteríaYa | Identificar tres errores del dominio y diseñar siete decisiones | E1: ejecución real, 10 fallos y 1 positivo; no se sembraron errores adicionales |
| 2 | ModeloInteractivo: leer ISSUE-01 | `leer_archivo(issues/ISSUE-01.md)` | Se conserva la respuesta literal en issue01-interactivo.json |
| 3 | Reproducir antes de editar | `ejecutar_pruebas(seleccion=01)` | Dos fallos: delivery omitido y sum vacío de tipo int |
| 4 | Inspeccionar el dominio | `leer_archivo(src/pedidos/dominio.py)` | Agregar campo al final conserva posiciones anteriores del dataclass |
| 5 | Corregir total sin acumular | Dos propuestas `editar_archivo`: campo Decimal y suma con inicial Decimal | Consola usada por Codex; dos pruebas verdes; aprobación humana no acreditada |
| 6 | Issue 3: localizar asignación | Mapa AST, búsqueda de self.disponible, anotar y recuperar hipótesis | Guardia antes de mutar; dos pruebas verdes, copia aislada |
| 7 | Issue 2: primer parche preparado con isinstance | El replay aplica `isinstance(cantidad, int)` | **Error detectado por tests:** True hereda de int. Es un error deliberadamente incluido en el experimento, no una respuesta espontánea de otro modelo |
| 8 | Crítico solicita corregir bool | Segunda ronda usa `type(cantidad) is not int` | Siete casos verdes; crítico no pudo editar tests/dominio por su rol |
| 9 | Reto B: Codex lee AGENTS y reproduce issue 3 | Edición real con apply_patch en copia independiente | Dos fallos antes; 52 pruebas del issue y regresión pasan después |

Los resúmenes describen decisiones operativas verificables, no razonamiento
interno privado del modelo. No se editan a mano decisiones inválidas para que
parezcan válidas: ModeloInteractivo guarda el texto recibido y el contrato lo
rechaza; test_interactivo_graba_invalido_sin_reescribir verifica esta propiedad.
