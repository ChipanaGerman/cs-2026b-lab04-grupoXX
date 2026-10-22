# Tabla de olores detectados — E1 PicanteríaYa

> Generada con **Prompt IA 1** (detector de olores) y verificada por el equipo contra `antes/servicio.py`.
> Herramienta: `radon cc -s -a src/pedidos/antes/servicio.py`

## Salida de radon (antes del refactor)

```
antes/servicio.py
    M 44:4 ServicioPedidos.confirmar_y_pagar - C (15)
    M 88:4 ServicioPedidos.asignar_repartidor - B (6)
    M 103:4 ServicioPedidos.sugerir_descripcion_plato - B (7)
    C 35:0 ServicioPedidos - B (10)
Average complexity: B (9.5)
```

## Tabla de olores detectados

| # | Líneas | Olor | Patrón GoF propuesto por la IA | Principio SOLID | Costo estimado | Decisión del equipo |
|---|--------|------|-------------------------------|-----------------|----------------|---------------------|
| 1 | 50–80 | `if/elif` por medio de pago que crece con cada nuevo método (YAPE, CULQI…) | **Strategy + Factory** | O — Abierto/Cerrado | Medio: crear interfaz `PasarelaPago`, 2 adaptadores y 1 fábrica | ✅ Aceptado — el negocio prevé agregar Plin y transferencias |
| 2 | 54, 68 | El servicio conoce detalles internos de cada SDK (dict, céntimos, tupla) | **Adapter** | D — Inversión de dependencias | Bajo: encapsular en `YapeAdapter` y `CulqiAdapter` | ✅ Aceptado — cada SDK tiene interfaz diferente |
| 3 | 53–60, 67–74 | Bloque de reintentos duplicado para Yape y Culqi | **Decorator** (`ConReintentos`) | S — Responsabilidad única | Bajo: 10 líneas de wrapper | ✅ Aceptado — elimina duplicación y facilita configurar intentos |
| 4 | 35–48 | Condicionales anidados sobre `pedido.estado` (`if estado != "RECIBIDO"…`) | **State** | O — Abierto/Cerrado | Alto: una clase por estado | ✅ Aceptado — coincide con la máquina de estados del Lab 05 |
| 5 | 82–88 | El servicio notifica "a mano" a WhatsApp y arma los mensajes inline | **Observer** | S — Responsabilidad única | Medio: `PublicadorEventos` + suscriptores | ✅ Aceptado — el negocio prevé agregar picantería y auditoría |
| 6 | 103–125 | `if/elif` por proveedor de LLM y validaciones mezcladas | **Strategy + Adapter + Chain of Responsibility** | D — Inversión de dependencias | Medio: interfaz `ProveedorLLM` + cadena de guardrails | ✅ Aceptado — la IA es componente no determinista; se aísla |
| 7 | — | IA propone: `FabricaPasarelas` como Singleton | **Singleton** | — | — | ❌ **Rechazado** — introduce estado global e impide inyectar SDKs simulados en pruebas |
| 8 | — | IA propone: Abstract Factory para "familias de pasarelas" | **Abstract Factory** | — | — | ❌ **Rechazado** — no hay familias de productos; sería sobreingeniería (solo 2 pasarelas) |

## Regla de oro aplicada

> La IA propone, el equipo decide y verifica. Los patrones 7 y 8 fueron rechazados porque no eliminan un olor concreto y añadirían complejidad innecesaria para el MVP de 1 mes.
