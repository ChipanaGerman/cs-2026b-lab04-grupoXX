# Matriz de entrega: Laboratorio 11 de Picantería Ya

Fecha de preparación: 24/11/2026, America/Lima. Fecha límite docente: sábado 28/11/2026, 23:59. La nota final la determina el docente; esta matriz vincula requisitos con evidencia sin declarar actividades externas ficticias.

| Criterio | Puntos | Evidencia |
|---|---:|---|
| E1 Catálogo | 2 | diseno/catalogo-mcp.md: tres herramientas justificadas, dos recursos, plantilla ADR y prompt; escritura de creación acotada |
| E2 Servidor | 4 | servidor_mcp/picanteria_mcp.py y src/pedidos/consultas_mcp.py: SDK oficial, stdio, reutilización del dominio, salida Pydantic, errores útiles y única escritura |
| E3 Contratos e Inspector | 3 | pruebas/test_servidor_mcp.py y pruebas/inspector.md con tres capturas reales |
| E4 Agente vía MCP | 3 | agente/README.md, ModeloInteractivo del Lab 10, trayectorias y trazas de negocio; error de fecha corregido y autorización explícita del usuario |
| E5 Host real | 2 | ../../.vscode/mcp.json, uso-en-host.md y trayectorias/host; cuatro consultas completadas (incluido prompt real) y quinta detenida en aprobación humana. **Pendiente: resultado final de escritura del host.** |
| E6 Protocolo | 2 | protocolo.md, JSONL real, generador, Mermaid/SVG/PNG, métricas y comparación real antes/después |
| E7 Seguridad y bitácora | 2 | seguridad.md, cliente/auditar.py, cinco pruebas del auditor, dos reglas nuevas, siete hallazgos de fixture y bitacora-ia.md |
| E8 ADR y entrega | 2 | ADR-011, sección del README, guía de ejecución y etiqueta v1.1-mcp; la entrega en Aula Virtual corresponde al grupo |
| Reto B MRTR | +2, máximo total 20 | reto/README.md, siete casos automatizados y confirmación humana real en E4; input_required seguido de complete |

## Validación

- 29 casos MCP (17 contratos base, 7 casos MRTR, 5 del auditor) en verde. Evidencia: pruebas/resultado-final.txt.
- 143 pruebas locales en verde incluyendo tests, agentes/pruebas_agente y agentes/mcp/pruebas. Algunos archivos de los Labs anteriores ya estaban sin versionar antes de esta tarea y se preservan; el commit de Lab 11 solo incorpora los módulos del núcleo necesarios para E4.
- Exportación aislada de los commits: 29 pruebas MCP en verde, ejecutadas con la carpeta exportada como directorio de trabajo. Confirma que el servidor no depende de los cambios previos sin commit.
- CI MCP en .github/workflows/mcp.yml usa las dependencias fijadas; la ejecución remota debe comprobarse después de push.
- Diagrama renderizado y revisado: etiquetas, mensaje de error, dos rondas de escritura y aprobación humana visibles.

## Actividades adicionales

Las ocho preguntas están resueltas en cuestionario.md. Preparación, demostración adaptada y checkpoint están en checkpoint.md. Por indicación del usuario, no se inventa intercambio con otro grupo ni se presenta como original la fixture recreada a partir de la guía. Si el docente exige esa actividad presencial, el grupo debe realizarla y registrar evidencia real.

## Git y entrega del grupo

Rama: codex/lab11-mcp. Un commit por ejercicio/actividad; autor gchipanaj@unsa.edu.pe y coautores lbacac@unsa.edu.pe y gmejiar@unsa.edu.pe. Los cambios previos en dominio, backlog y README del Lab 10 se mantienen fuera de los commits del Lab 11.

Tras revisar el PR y los checks, un integrante distinto del autor debe revisar y fusionar según las reglas del equipo. No se realiza autofusión. Entregar el enlace del repositorio y la etiqueta v1.1-mcp en el Aula Virtual antes del plazo. La publicación en Aula Virtual no se ha realizado desde este entorno.
