# E5: conexión real a VS Code con GitHub Copilot

## Entorno verificado el 24/11/2026

El VS Code instalado (1.98.2) no ofrecía MCP: List Servers. Se descargó desde update.code.visualstudio.com una copia oficial temporal 1.147.0 en tmp/mcp/vscode; no se reemplazó la instalación. Se abrió la carpeta con la sesión existente de Copilot. La configuración del equipo está en ../../.vscode/mcp.json y no contiene claves.

MCP: List Servers → picanteria-ya → Start Server. El registro local indicó Running y «Discovered 3 tools». Ese conector del editor usa initialize por compatibilidad, mientras la ejecución E4 y el reto usan protocolo 2026-07-28 por petición. No se presupone que todas las conexiones de un host negocien la misma versión.

Para reproducir: crear .venv-mcp e instalar requirements-lock.txt, abrir la raíz con un VS Code compatible, seleccionar Copilot/Agent, iniciar el servidor y revisar herramientas. Conservar los permisos manuales; no seleccionar aprobación automática global.

## Consultas y resultados observados

| # | Consulta | Primitiva elegida | ¿Permiso? | Resultado y evidencia |
|---|---|---|---|---|
| 1 | «Consulta el menú de La Tradición del 2026-11-24 exclusivamente mediante MCP» | menu_del_dia, tras Search Tools | Sin diálogo de escritura | Rocoto S/25.00, stock 12; chupe S/35.50, stock 8. Correcto. trayectorias/host/01-menu.txt |
| 2 | «Consulta pedidos CANCELADO; devuelve UUID y total» | pedidos_por_estado | Sin diálogo de escritura | 00000000-0000-0000-0000-000000000001, S/25.00. Correcto. 02-cancelados.txt |
| 3 | «Lee picanteria://zonas y dime los distritos de delivery» | Read MCP resource, URI picanteria://zonas | Sin diálogo de escritura | Yanahuara, Cayma y Cercado. Correcto. 03-zonas.txt |
| 4 | «Responder reclamo: Pedido cancelado sin explicación», invocando la plantilla del servidor | /mcp.picanteria-ya.responder_reclamo, argumento descripcion | No hay escritura | Se recuperó la plantilla real y el modelo respondió con empatía, pidió UUID y no inventó reembolsos. 04-prompt-recuperado.png y 04-prompt-local.txt |
| 5 | «Solicita registrar reclamo del pedido 00000000-0000-0000-0000-000000000001 con texto Verificación de atención desde Copilot; pedido cancelado sin explicación.» | registrar_reclamo | **Sí: Allow Once y formulario Confirmo crear este reclamo → Yes** | Creado 7b735b41-7c7d-4b56-85c9-174b1f000336 tras autorización expresa del usuario. 05-reclamo-creado.txt/.png y 05-aprobacion.json |

## Compatibilidad del prompt

Un primer intento de solicitar prompts/get en la experiencia Copilot nueva terminó informando que no dispone de esa operación. No se sustituyó por texto inventado. La documentación oficial confirma que el picker de prompts MCP del editor no se expone en esas sesiones.

Se abrió Chat: New Chat Editor, se eligió Local (la experiencia anterior del mismo VS Code con Copilot), se escribió `/mcp.picanteria-ya.responder_reclamo`, se activó la sugerencia con Ctrl+Espacio y se introdujo descripcion como **Insert as text**, nunca Run as Command. El host recuperó y mostró el texto devuelto por el servidor, que luego se envió al modelo. La respuesta observada pide el identificador necesario para verificar el reclamo, sin prometer reembolso.

Fuentes: [soporte MCP y compatibilidad Local](https://code.visualstudio.com/api/extension-guides/ai/mcp) y [selección de experiencia del agente](https://code.visualstudio.com/docs/agents/run/agent-harnesses). Local está deprecado para febrero de 2027; se utilizó aquí para verificar el requisito concreto de prompts del laboratorio, no como recomendación de arquitectura permanente.

![Plantilla MCP recuperada en Local](trayectorias/host/04-prompt-recuperado.png)

## Escritura confirmada y resultado verificado

La consulta 5 se detuvo primero en el permiso del host. El usuario respondió en este chat «Sí, autorizar ese segundo reclamo» para el pedido y texto exactos. El asistente transmitió esa decisión mediante **Allow Once**, sin habilitar permisos de sesión, y luego **Yes** en el formulario «Confirmo crear este reclamo». La autorización anterior de E4 no se reutilizó.

![Permiso previo a la creación en Copilot](trayectorias/host/05-permiso-pendiente.png)

El host mostró el formulario MRTR y su registro accesible conserva **Answered: Yes**. La herramienta devolvió el UUID 7b735b41-7c7d-4b56-85c9-174b1f000336 y se comprobó el JSON local creado: pedido, descripción y UUID coinciden exactamente. No se modificaron pedidos ni pagos. En este formulario de una sola pregunta, seleccionar Yes completó el envío automáticamente; no se inventa un clic adicional en Submit.

![Resultado del reclamo confirmado](trayectorias/host/05-reclamo-creado.png)

La respuesta narrativa de Copilot dijo erróneamente que no apareció confirmación humana. Se conserva esa salida sin corregirla artificialmente: contradice el diálogo observado y el registro **Chat question / Confirmo crear este reclamo / Answered: Yes**. La evidencia de consentimiento es la autorización explícita del usuario y la interfaz del host, no la interpretación del modelo sobre una UI que no controla. Las cinco consultas requeridas quedaron completadas, incluido el prompt del servidor y la escritura confirmada.
