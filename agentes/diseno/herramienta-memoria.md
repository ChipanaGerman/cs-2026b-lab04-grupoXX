# E4. Herramienta y memoria

`mapa_repo()` analiza con `ast.parse` todos los Python de `src/` y devuelve
rutas, líneas y firmas sin importar módulos. `anotar(texto)` escribe una nota
de hasta 2000 caracteres en `notas.md` del sandbox; el acumulado no supera
8000. `leer_notas()` recupera las hipótesis entre decisiones o instancias.
Catálogo ejecutable y contratos: `agente/herramientas.py`.

La memoria de notas es una pizarra persistente por tarea, distinta del historial
de corto plazo del modelo. No es memoria episódica global ni una base vectorial.
Los errores de AST, rutas y límites vuelven como observaciones.

ISSUE-03 se resolvió con `mapa_repo`, búsqueda de `self.disponible`, una nota,
lectura de notas, prueba roja, guardia previa a la mutación y prueba verde.
La traza `issue03-notas.jsonl` registra 9 decisiones frente a 7 en E2;
el contexto final inicial medido fue 14135 frente a 16785 caracteres.
Las notas no redujeron pasos: agregaron dos acciones. El mapa evitó leer
todo el dominio. La comparación usa issues diferentes y no permite atribuir
causalmente la reducción de contexto a la memoria. Las cifras actualizadas
se calculan en `observacion.md` directamente desde las trazas.

Reproducción: `python -m agentes.experimentos`. Las aprobaciones de esta
reproducción son fixtures automáticos expresamente identificados; para
intervención humana real usar el modo interactivo de `ejecutar.py`.
