# Cuestionario del laboratorio 10

1. **Agente frente a flujo fijo.** El agente elige qué inspeccionar según las
   observaciones. Un flujo fija todos los pasos. En PicanteríaYa validar una
   cantidad y sumar el delivery son reglas deterministas; no deben depender
   de una decisión lingüística durante un cobro.
2. **Dos arquetipos.** ReAct para ISSUE-01 y ISSUE-03: localizar total y
   asignación requiere explorar y verificar. Planificador-ejecutor con reflexión
   para ISSUE-02: separar análisis de tipos, edición y crítica. Las tres tareas
   podrían corregirse sin agentes si ya se conoce exactamente la causa.
3. **Estados y guardia.** INICIO, DECIDIENDO, VALIDANDO_CONTRATO,
   EVALUANDO_POLITICA, ESPERANDO_APROBACION, EJECUTANDO y OBSERVANDO, con
   CONTRATO_INVALIDO, BLOQUEADO, FINALIZADO y LIMITE_ALCANZADO. El `range`
   acota todas las decisiones, incluso inválidas: 12 actor, 8 crítico y dos
   rondas máximo. El agotamiento del modelo también termina la tarea.
4. **Contrato.** Un objeto con pensamiento y acción/args o final, tipos
   correctos y campos cerrados. El rechazo vuelve como observación sin
   ejecutar herramientas. En las pruebas propias se usa args como texto y
   una herramienta inventada. E2 no produjo rechazos espontáneos; no se
   inventa uno para la bitácora. El error real del parche fue aceptar bool.
5. **Memoria.** Pizarra persistente por tarea en notas.md, además del historial
   de corto plazo. E4 usó 9 decisiones y 14135 caracteres, frente a 7 y 16785
   en E2. Añadir notas no redujo pasos; mapa y distinta tarea explican parte
   de la diferencia. No hay evidencia de un efecto causal aislado.
6. **Coordinación.** E5: único 7 acciones y 19511 caracteres; gestor y dos
   rondas actor-crítico 10 acciones y 25277 caracteres finales sumados. Ambos
   llegaron al mismo parche. El crítico detectó bool y se bloqueó su escritura,
   pero el único también lo detectó mediante tests. Para este alcance no
   compensa el costo adicional: parsimonia favorece un agente y revisión humana.
7. **Exceso de agencia.** Dar herramientas o autonomía que el rol no necesita.
   El crítico no escribe; el actor solo edita dominio.py con aprobación. No hay
   shell libre, red, credenciales ni escritura en tests. Las rutas se resuelven
   dentro de la copia. Esto es confinamiento de herramientas, no un aislamiento
   de procesos del sistema operativo para ejecutar código hostil arbitrario.
8. **Etapa actual.** Revisor: una persona debe examinar cada edición y el PR.
   Para avanzar a colaborador se exigirían diez tareas sin regresiones,
   rechazos demostrados, costos observados y revisión independiente. Las
   aprobaciones de replay y las respuestas introducidas por Codex no cuentan
   como esa validación humana. Ver delegacion.md.
