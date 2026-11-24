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
| 5 | «Solicita registrar reclamo del pedido 00000000-0000-0000-0000-000000000001 con texto Verificación de atención desde Copilot; pedido cancelado sin explicación.» | registrar_reclamo | **Sí: Allow tool from picanteria-ya?** | **Pendiente de respuesta humana. No se creó el segundo reclamo.** 05-permiso-pendiente.txt y .png |

## Compatibilidad del prompt

Un primer intento de solicitar prompts/get en la experiencia Copilot nueva terminó informando que no dispone de esa operación. No se sustituyó por texto inventado. La documentación oficial confirma que el picker de prompts MCP del editor no se expone en esas sesiones.

Se abrió Chat: New Chat Editor, se eligió Local (la experiencia anterior del mismo VS Code con Copilot), se escribió `/mcp.picanteria-ya.responder_reclamo`, se activó la sugerencia con Ctrl+Espacio y se introdujo descripcion como **Insert as text**, nunca Run as Command. El host recuperó y mostró el texto devuelto por el servidor, que luego se envió al modelo. La respuesta observada pide el identificador necesario para verificar el reclamo, sin prometer reembolso.

Fuentes: [soporte MCP y compatibilidad Local](https://code.visualstudio.com/api/extension-guides/ai/mcp) y [selección de experiencia del agente](https://code.visualstudio.com/docs/agents/run/agent-harnesses). Local está deprecado para febrero de 2027; se utilizó aquí para verificar el requisito concreto de prompts del laboratorio, no como recomendación de arquitectura permanente.

![Plantilla MCP recuperada en Local](trayectorias/host/04-prompt-recuperado.png)

## Escritura: estado exacto

La consulta 5 se detuvo en el permiso del host antes de invocar la herramienta. El asistente pidió al usuario autorización concreta para ese segundo registro y dejó el diálogo sin aceptar. La autorización anterior de E4 ya se utilizó para crear el primer reclamo y no se presenta como una segunda confirmación.

![Permiso de escritura pendiente en Copilot](trayectorias/host/05-permiso-pendiente.png)

Para finalizar: el usuario debe aprobar o rechazar ese permiso. Si aprueba, el cliente invoca la herramienta y, en una conexión 2026-07-28, el servidor devuelve input_required; el host debe mostrar además el formulario de confirmación del contenido. Aceptarlo solo para ese reclamo y conservar el resultado real y su UUID. Si el host negocia una versión antigua, el servidor rechaza la escritura con un error útil: usar una conexión moderna, nunca retirar el control para aparentar éxito.

La prueba humana completa de MRTR **sí se ejecutó en E4**. La quinta consulta del host, en cambio, queda sin resultado final mientras falte la aprobación. Por ello no se declara E5 al 100 % ni se contabiliza una escritura del host que no ocurrió.
