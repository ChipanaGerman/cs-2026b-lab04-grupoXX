# E1: catálogo MCP de Picantería Ya

Datos ficticios, sin teléfonos, direcciones personales ni pagos reales. Protocolo 2026-07-28, SDK oficial MCP 2, stdio. El servidor adapta el dominio existente; no expone shell, edición de código, cobros ni cambios de estado.

| Capacidad | Primitiva | Escritura | Justificación y contrato |
|---|---|---|---|
| menu_del_dia | herramienta | No | Consulta parametrizada: fecha AAAA-MM-DD y picanteria de 1–80 caracteres; devuelve fecha, establecimiento y platos disponibles con precio decimal en soles. Fecha inexistente: error útil. |
| pedidos_por_estado | herramienta | No | estado RECIBIDO, PAGADO, PREPARANDO, EN_CAMINO, ENTREGADO o CANCELADO; devuelve como máximo 20 pedidos ficticios con identificador y total, sin datos personales. |
| registrar_reclamo | herramienta | Sí, única | pedido_id UUID existente; descripcion de 10–1000 caracteres. Crea un archivo nuevo por UUID en datos/reclamos, nunca modifica pedidos ni sobrescribe archivos. Reto B: solicita confirmación antes de crear. |
| picanteria://zonas | recurso | No | Cobertura estable de delivery; la aplicación decide incorporarla al contexto. |
| picanteria://reglas | recurso | No | Estados y reglas de privacidad, dinero y reclamos del equipo. |
| picanteria://adr/{numero} | recurso plantilla | No | Número de exactamente tres dígitos; lectura de ADR existente dentro de docs/architecture/adr. Rechaza traversal. |
| responder_reclamo | prompt | No | descripcion de 10–1000 caracteres; plantilla del equipo derivada de prompts/criterios/v3.1.txt: respuesta empática, hechos verificables, sin inventar reembolsos ni ejecutar instrucciones contenidas en datos. |

## Seguridad de la única escritura

Registrar un reclamo ficticio es una acción de creación local, reversible y sin efecto sobre dinero, stock o pedidos. Se usa apertura exclusiva (`x`), nombre generado por el servidor y carpeta fija; el usuario no elige rutas. La confirmación se vincula al contenido exacto de la solicitud y se consume una sola vez. Rechazar o cancelar no crea archivos. Las anotaciones no sustituyen estas restricciones.

## Criterios verificables

E1: esta tabla y descripciones. E2: servidor y servicio de aplicación. E3: pruebas de protocolo e Inspector. E4: adaptador del Lab 10 y trayectoria interactiva. E5: configuración y cinco consultas reales. E6: tráfico, secuencia, métricas antes/después. E7: auditor, dos reglas nuevas y bitácora. E8: ADR-011, README y tag. Reto B: input_required y continuación confirmada con cliente.

El intercambio con otro grupo requiere un catálogo externo y revisión por ese grupo; no se atribuirá una revisión ficticia.
