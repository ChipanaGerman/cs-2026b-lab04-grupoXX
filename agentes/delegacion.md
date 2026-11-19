# E6. Humano en el circuito

`Politica.aprobar_edicion` utiliza `aprobar_consola` por defecto. Antes de cada
edición muestra ruta, antes y después, y exige `s` o `n`; otra entrada repite
la pregunta. EOF, rechazo o interrupción impiden escribir. El control registra
ESPERANDO_APROBACION y BLOQUEADO u OBSERVANDO. La aprobación del crítico jamás
fusiona cambios ni sustituye a una persona.

| Etapa humana | Permisos del agente | Evidencia para avanzar |
|---|---|---|
| Ejecutor | Solo lectura; humano aplica cambios y ejecuta pruebas | Tres reproducciones correctas y cero escapes de sandbox |
| Revisor (etapa actual) | Proponer fragmentos y probar en copia; cada edición requiere s/n | Tres issues verdes, contratos y rechazos efectivos; revisión independiente de los diffs |
| Colaborador | Editar únicamente dominio en rama aislada dentro de un alcance aprobado; PR siempre humano | Diez tareas revisadas sin regresiones, costos medidos, rechazo y recuperación demostrados |
| Gobernador | Automatizar tareas repetitivas acotadas con auditoría y revocación; sin pagos reales, secretos ni fusión autónoma | Historial sostenido, alertas y reversión probada; decisión explícita del equipo |

## Qué se ejecutó realmente

E2 usó consola real, pero los `s` los introdujo Codex bajo autorización de
trabajo del usuario. E4 y E5 usan `replay_aprobado`, un fixture automatizado,
identificado como tal. Las pruebas cubren respuesta inválida, aceptación,
rechazo y EOF. Esto verifica el mecanismo y no acredita que una persona
del grupo haya aprobado cada edición. Esa demostración presencial permanece
pendiente: no se sustituye por una aprobación inventada.

## Demostración por un integrante

Desde la raíz: `python -m agentes.orquestador` (sin --replay-aprobado).
Responder primero una entrada inválida y luego `n` para observar el bloqueo.
Repetir la ejecución y revisar cada fragmento antes de escribir `s`.
Revisar trazas y pruebas; firmar la decisión en el PR. El modo interactivo
del issue 1 se ejecuta con `python -m agentes.ejecutar --issue 01 --salida issue01-humano`.
Las nuevas trazas se guardan con su procedencia; no deben renombrarse como
si pertenecieran a las ejecuciones previas.
