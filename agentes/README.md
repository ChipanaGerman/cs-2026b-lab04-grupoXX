# Laboratorio 10: PicanteríaYa

## Instalación y verificación

Desde la raíz del repositorio, Python 3.10 o posterior:

```bash
python -m pip install -r prompts/requirements.txt pytest
python -m pytest -q tests agentes/pruebas_agente
python -m agentes.experimentos
python -m agentes.orquestador --replay-aprobado
python -m agentes.reportar
```

La última orden requiere Java y el `plantuml.jar` existente. Produce Mermaid,
PlantUML equivalente y PNG desde los mismos eventos JSONL; la máquina de
estados se mantiene en `diseno/estados.puml`. No requiere claves ni LLM en CI.
Los replays sobre copias de la base no modifican el dominio final del proyecto.

## Modo interactivo y aprobación real

```bash
python -m agentes.ejecutar --issue 01 --salida issue01-humano
python -m agentes.orquestador
```

Copiar CONTEXTO_ACTUAL al asistente, solicitar una sola decisión JSON y pegarla
en una línea. El protocolo tiene estas dos formas exclusivas:

```json
{"pensamiento":"Leer el issue","accion":"leer_archivo","args":{"ruta":"issues/ISSUE-01.md"}}
```

```json
{"pensamiento":"Pruebas verificadas","final":"Resumen y pendientes"}
```

No corregir manualmente las decisiones inválidas: el contrato las devuelve al
modelo. Para cada edición, una persona revisa antes/después y responde s/n.
El máximo de pasos incluye respuestas inválidas. Reproducir decisiones de E2:

```bash
python -m agentes.ejecutar --issue 01 --replay agentes/trayectorias/issue01-interactivo.json --salida issue01-replay-humano
```

Ese replay también requiere aprobación por consola. `--replay-aprobado` solo
existe para la comparación automatizada del orquestador y se identifica como
fixture. No constituye una aprobación humana.

## Mapa de entregables

* E1: diseno/lienzo.md, ../issues/, ../tests/test_issue_*.py y evidencia/E1-rojo.txt.
* E2: ejecutar.py, agente/, trayectorias/issue01-interactivo.json y trazas/.
* E3: diseno/estados.puml, estados.png y pruebas_agente/test_control.py.
* E4: diseno/herramienta-memoria.md, experimentos.py y pruebas de notas/AST.
* E5: orquestador.py y observacion.md (comparación agregada y conclusión).
* E6: delegacion.md y agente/politica.py.
* E7: observacion.md, bitacora-ia.md, reportar.py y evidencia/metricas.json.
* E8: ../docs/architecture/adr/010-sistema-agentico.md, README y entrega.md.
* Cuestionario: cuestionario.md. Reto B: reto/README.md y reto/AGENTS.md.

El framework es una implementación propia basada en los extractos de la guía;
no se recibió el archivo de recursos externo. La ejecución comercial del reto
se realizó con Codex de esta sesión, sin atribuirla a Claude Code/Copilot/Gemini.
