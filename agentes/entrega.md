# Entrega y matriz de verificación

Fecha límite de la guía: sábado 21/11/2026, 23:59.

| Criterio | Puntos | Evidencia | Estado |
|---|---:|---|---|
| E1: siete decisiones y tres pruebas rojas | 3 | diseno/lienzo.md, issues, evidencia/E1-rojo.txt | Implementado y ejecutado |
| E2: ReAct interactivo, traza y verde | 3 | issue01-interactivo.json/.jsonl/.mmd/.png | Ejecutado por Codex con registro literal |
| E3: estados fieles y contratos propios | 3 | diseno/estados.*, pruebas_agente/test_control.py | Implementado y probado |
| E4: herramienta y notas con medición | 2 | herramienta-memoria.md, issue03-notas.*, test_memoria.py | Ejecutado; efecto medido sin inferir causalidad |
| E5: comparación y conclusión | 3 | observacion.md, trazas issue02-* | Mismo parche; dos rondas; datos reales |
| E6: aprobación y delegación | 2 | politica.py, delegacion.md, pruebas de rechazo/EOF | Mecanismo probado; demostración por integrante pendiente |
| E7: métricas y cinco interacciones | 2 | observacion.md, bitacora-ia.md, metricas.json | Completado con procedencia explícita |
| E8: ADR, README, tag y enlace | 2 | ADR-010, README, workflow agentes.yml | Archivos listos; verificar tag y entregar enlace |
| Reto B | +2 (tope 20) | reto/AGENTS.md, codex.diff, rojo/verde y comparación | Ejecutado con Codex; validar equivalencia con ejemplos de la guía si el docente lo exige |

## Revisión cruzada y checkpoint

La guía pide revisión de otro grupo y registro de observaciones en su repositorio.
No se proporcionó ese repositorio ni se realizó una revisión por otro grupo.
No se inventa el checkpoint del docente ni una revisión externa. Para completarlos:
compartir lienzo y trayectoria, recibir observaciones, registrar el issue real
en el repositorio revisado y enlazarlo aquí junto con la respuesta del equipo.

## Flujo de GitHub

Rama de entrega: codex/lab10-sistemas-agenticos. Un commit por E1–E8 y otro
por reto B, todos con los tres correos de coautoría. Se mantienen Grupo XX y
el nombre actual del repositorio: no se recibió un número de grupo distinto.
La carpeta .git local está protegida, por lo que los commits se publicaron
por la API de GitHub sin tocar los cambios previos del Lab 09.

El PR se deja abierto para revisión humana y no se fusiona automáticamente.
El workflow valida las pruebas y, en el commit final cuyo mensaje empieza
por `Reto B:`, crea la etiqueta `v1.0-agentes` sin sobrescribir otra etiqueta.
Esta etiqueta identifica la entrega propuesta, no una aprobación del docente.

Si Actions no puede crearla, desde un clon con permisos normales:

```bash
git fetch origin
git switch --track origin/codex/lab10-sistemas-agenticos
python -m pytest -q tests agentes/pruebas_agente
git tag v1.0-agentes
git push origin refs/tags/v1.0-agentes
```

Comprobar previamente que la etiqueta no existe. El integrante revisa y aprueba
el PR; después se entrega el enlace en Aula Virtual. Estas acciones humanas
no se registran como completadas por el asistente.
