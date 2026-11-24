# Cuestionario del Laboratorio 11

1. **Problema de integración.** Si Copilot, el agente del Lab 10 y otro asistente necesitan menú, pedidos y reclamos, una integración específica por pareja requiere 3×3=9 adaptadores. MCP permite tres clientes compatibles y tres capacidades publicadas una vez: N+M=6 piezas conceptuales. En este proyecto un único servidor agrupa las tres capacidades; la fórmula ilustra la reducción de acoplamiento, no cuenta procesos ni funciones concretas.

2. **Roles.** El host es Copilot o nuestro agente: usa el modelo, construye contexto y gestiona permisos. El cliente mantiene la conexión y serializa JSON-RPC. El servidor Picantería Ya expone las capacidades del negocio sin depender del modelo. Un host conectado a tres servidores necesita tres clientes/conexiones lógicas.

3. **Herramienta y recurso.** Una consulta de ventas o pedidos depende de filtros que el modelo elige: es una herramienta. Un ADR es contexto estable identificado por URI: es un recurso que incorpora la aplicación. Los prompts los invoca el usuario. Una anotación readOnlyHint no transforma una herramienta en recurso.

4. **Ciclo de vida 2026-07-28.** En lugar de initialize y sesión negociada, cada petición declara versión y capacidades en _meta; server/discover anuncia capacidades/versiones. Una instancia remota puede atender la petición autocontenida sin recuperar una sesión del balanceador. Las operaciones con estado de negocio, como la confirmación, aún necesitan estado explícito; el prototipo stdio usa requestState autenticado y confirmaciones temporales locales.

5. **Errores.** isError=true es un resultado de herramienta: la invocación pudo entregarse pero la fecha o estado eran inválidos. El agente puede leer la explicación y corregirse, como 24/11/2026 → 2026-11-24 en E4. Un error JSON-RPC describe un fallo de protocolo, método o parámetros, como -32601 para método inexistente o -32602 para requestState inválido; se procesa en otra rama del cliente. Ambos deben manejarse, pero el ejemplo de autocorrección de negocio usa isError.

6. **Anotaciones.** Las declara el servidor y pueden mentir; no son un control de acceso. El catálogo marca dos lecturas y una escritura no destructiva. La política permite solo esas capacidades y el adaptador exige confirmación MRTR para la escritura. El servicio limita la operación a crear un archivo nuevo, independientemente de las pistas declaradas.

7. **Contexto medido.** El catálogo completo pasó de 2513 caracteres y 2518 bytes a 2473 caracteres y 2476 bytes. Se acortaron descripciones preservando contratos y outputSchema. ceil(caracteres/4) estima 629 → 619 tokens, reducción de 1,59 %. No equivale al tokenizer ni al contexto total del host. Ver protocolo.md y los catálogos capturados.

8. **Envenenamiento.** Una descripción aparentemente útil puede esconder instrucciones para leer secretos o enviarlos a terceros. Aplicar: revisión del catálogo y del código antes de conectar; lista permitida de servidores/versiones y datos accesibles mínimos; aprobación humana de escritura y ausencia de credenciales en su alcance. El auditor detectó siete señales en la fixture inerte de clima y no la conectó a un LLM. Los patrones no garantizan detectar ataques ofuscados.
