# Reto adicional, opción B: Codex frente al agente propio

## Configuración y procedencia

Se resolvió ISSUE-03 con **Codex en esta sesión de Work Mode**, usando las
herramientas de lectura, terminal y apply_patch. No se ejecutó Claude Code,
Copilot ni Gemini CLI, ni se atribuye a ellos esta evidencia. El AGENTS.md de
esta carpeta fijó alcance, pruebas inmutables, restricción de red y revisión.

La copia comercial partió de `../fixtures/dominio_base.py.txt`, igual que el
agente propio de E4. Se copiaron src/tests/issues y pytest.ini a un sandbox
independiente. Las pruebas no se alteraron. El sandbox temporal se retiró
después de guardar salidas y diff para evitar duplicar el proyecto.

## Trayectoria comercial real

| Invocación de herramienta | Operaciones | Resultado observado |
|---:|---|---|
| 1 | Preparar copia; leer AGENTS.md y ISSUE-03 | Alcance: no reasignar un repartidor ocupado ni mutar pedido al rechazar |
| 2 | Ejecutar pytest del issue; inspeccionar Repartidor | Dos fallos; asignar_pedido no consultaba disponible |
| 3 | apply_patch sobre el dominio de la copia | Guardia previa; preparar pedido antes de marcar repartidor ocupado |
| 4 | Ejecutar pruebas de issue y regresiones; generar diff y comparar tests | 52 passed; pruebas intactas |

Registro estructurado: `trayectoria-codex.json`. Evidencias completas:
`codex-rojo.txt`, `codex-verde.txt`, `codex.diff`, `codex-dominio.py.txt`.
Estas cuatro invocaciones están agrupadas: no equivalen a cuatro decisiones
del mini framework. La cuenta no incluye la documentación de esta comparación.

## Comparación con E4

| Dimensión | Agente propio, issue03-notas | Codex comercial |
|---|---|---|
| Punto de partida | Misma copia del dominio base y mismos tests | Misma copia del dominio base y mismos tests |
| Decisiones/operaciones | 9 decisiones JSON, 8 acciones | 4 invocaciones de herramientas agrupadas |
| Exploración | Mapa AST, búsqueda y notas | Lectura de instrucciones y fragmento de Repartidor |
| Memoria | Historial y notas.md persistente | Contexto de esta sesión; AGENTS.md procedimental |
| Resultado | Dos pruebas del issue pasan | Dos del issue y 50 de regresión pasan |
| Parche | Guardia ocupado antes de mutar; actualización de disponibilidad tras preparar | Mismo parche |
| Contexto final | 14135 caracteres del historial JSON | No expuesto por esta interfaz; no se inventa una cifra |
| Aprobación | Fixture de replay, no humana | Autorización general del usuario; revisión humana del PR pendiente |

Codex agrupó lectura, ejecución y comparación, mientras el agente propio exige
una decisión por herramienta. La diferencia de conteos no demuestra que uno
sea más eficiente en tokens o tiempo. El framework propio permite auditar
contrato, política y estados de cada paso; Codex reduce la implementación
necesaria y cuenta con herramientas generales, cuyo control depende del
entorno y de las instrucciones. Ambos llegaron al mismo cambio mínimo.

La corrección protege el modelo secuencial de dominio. Una implementación
con persistencia concurrente requeriría bloqueo o actualización transaccional
para impedir asignaciones simultáneas; no se afirma haber resuelto esa capa.
