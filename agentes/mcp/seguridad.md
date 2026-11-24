# E7: auditoría y mínimo privilegio

Ejecutar `.venv-mcp/Scripts/python -B -m agentes.mcp.cliente.auditar`. Evidencias: trazas/auditoria.json y auditoria-{propio,tercero_fixture}.jsonl. Se lee tools/list por stdio; no se ejecutan herramientas del servidor ajeno ni se conecta esa muestra a un host con LLM.

El archivo original de recursos no fue proporcionado. terceros/clima_mcp.py es una fixture educativa recreada a partir del patrón descrito por el docente, identificada expresamente como tal, sin lectura de archivos, red o credenciales. No se afirma que se auditó el archivo original.

## Resultado real

Servidor propio: cero hallazgos de estas reglas. Fixture de terceros: siete hallazgos: instrucciones ocultas (alta), solicitud de secretos (alta), acceso a .env ajeno al clima (media), parámetro genérico contexto (media), ausencia de anotaciones (baja), escritura potencial sin destructiveHint (alta) y texto sin límite (media).

Regla nueva 1: toda herramienta que no declare readOnlyHint=true y omita destructiveHint produce alerta. No supone que false haga segura la herramienta: obliga a revisar su semántica.

Regla nueva 2: string de entrada sin maxLength, enum o const produce alerta; también recorre objetos, listas y anyOf. Es una verificación de catálogo, no prueba de validación en ejecución. No resuelve referencias externas ni detecta todas las formas de ofuscación.

Pruebas: pruebas/test_auditor.py cubre ambas reglas, texto anidado, catálogo acotado y el patrón combinado de poisoning.

## Lista de verificación

- [x] Solo tres herramientas: dos consultas y una creación de reclamo.
- [x] Sin herramienta genérica de shell, archivos arbitrarios, pagos o cambios de estado.
- [x] Entradas acotadas con Field y validación de negocio; fecha real, estado permitido y UUID de pedido existente.
- [x] Dinero mediante Decimal y salida en cadena decimal para no introducir error binario.
- [x] Recursos limitados a URI conocidas; ADR de tres dígitos y ruta resuelta contenida en su carpeta; rechazo de traversal incluso codificado en pruebas.
- [x] Datos sintéticos sin teléfonos, ubicación precisa ni direcciones personales.
- [x] Sin API keys en código ni configuración; stdio local no requiere credenciales de un proveedor LLM.
- [x] Creación con nombre UUID y apertura exclusiva; no sobrescribe, borra ni modifica pedidos.
- [x] Permiso humano mediante MRTR: texto visible, token autenticado por SDK, cinco minutos de vigencia, vinculación al contenido y consumo único.
- [x] Auditoría del catálogo ajeno antes de conectar: la fixture se rechaza y nunca llega a un LLM.
- [x] Versiones directas fijadas; requirements-lock.txt registra las transitivas instaladas.

## Límites y decisión

Cero alertas no equivale a seguridad completa: el auditor por patrones puede omitir instrucciones indirectas u ofuscadas. Combinarlo con revisión humana del código y catálogo, versiones fijas y una lista de servidores aprobados. Lista del prototipo: picanteria-ya, SDK mcp 2.3.0, stdio local; clima-ficticio-no-confiable queda rechazado. HTTP no está habilitado y requeriría diseño de autenticación, autorización, cuotas y almacenamiento compartido del estado de confirmación.

El cliente es responsable de recabar una respuesta humana auténtica: un booleano enviado por un cliente malicioso no demuestra consentimiento. En E4 se conserva la autorización explícita del usuario de este chat y su transmisión al formulario. En pytest, las aceptaciones son fixtures, no evidencia humana.
