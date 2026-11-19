# ADR-010: Sistema agéntico de mantenimiento de PicanteríaYa

Fecha: 19/11/2026. Estado: propuesto para revisión humana.

## Contexto

El dominio omite delivery, admite cantidades inválidas y reasigna repartidores
ocupados. Se requiere explorar código y justificar cambios con pruebas.
La guía exige trabajo sin claves de API, trazas, límites y humano en el circuito.

## Decisión

Usar un mini framework propio basado en los extractos del ejemplo docente
(el archivo de recursos no estaba en la carpeta). Modelo es una Strategy:
ModeloInteractivo recibe JSON de un asistente y ModeloGrabado reproduce
decisiones guardadas. No se presenta el replay como razonamiento autónomo.

ReAct con contrato estricto y máquina de estados controla cada decisión.
Herramientas acotadas para lectura, búsqueda, edición, pytest, diff, mapa AST
y notas. El dinero sigue siendo Decimal; los agentes no participan en cobros.
Cada experimento trabaja en copia de src/tests/issues. Solo dominio.py puede
editarse. El catálogo no expone shell ni credenciales. El crítico y el gestor
son de solo lectura. Notas por tarea y un historial forman la memoria.

Se compararon agente único y gestor/actor-crítico, máximo dos rondas, con
12 decisiones por actor, 8 por crítico y 4 por gestor. El rechazo de contrato
también consume presupuesto. La aprobación por consola es obligatoria en el
modo normal; el modo de experimentos utiliza fixtures explícitos. Ningún
agente fusiona el PR; el humano conserva revisión y decisión final.

## Alternativas

* Flujo fijo: preferido para reglas del negocio y CI; insuficiente para explorar
  ubicaciones desconocidas. Sigue siendo la opción más simple para estos bugs
  cuando su causa ya está localizada.
* Un LLM con shell irrestricto: rechazado por exceso de agencia y falta de
  límites verificables.
* Framework externo y API pagada: descartado para mantener reproducción sin
  claves y entender el control. No se afirma equivalencia con producción.
* Multiagente permanente: descartado para estas correcciones pequeñas. E5
  produjo el mismo parche con más acciones y contexto acumulado.
* Coordinación democrática del reto A: no elegida; el equipo pidió reto B con Codex.

## Consecuencias y evidencia

Las trazas permiten reconstruir acciones, fallos, permisos y presupuestos.
Hay más código de control y las decisiones grabadas limitan adaptabilidad.
Las métricas miden caracteres y acciones, no latencia de inferencia ni tokens
facturados. No se exponen pensamientos privados del modelo: solo resúmenes
operativos de las decisiones del protocolo.

Ver agentes/observacion.md, agentes/delegacion.md y agentes/reto/README.md.
El confinamiento de rutas no sustituye una VM/contenedor para código hostil.
La asignación simultánea de repartidores requeriría transacción/lock en una
persistencia real; esta corrección solo cubre el modelo secuencial existente.
Pendientes externos: aprobación humana, revisión cruzada con otro grupo y
entrega del enlace en Aula Virtual. No se registran como realizadas.
