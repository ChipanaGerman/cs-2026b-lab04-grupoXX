# ADR-005: Patrones de diseño en el módulo Pedidos

- **Estado:** Aceptado
- **Fecha:** 21/10/2026
- **Autores:** Equipo PicanteríaYa (Lab 07)
- **Contexto:** Lab 07 — Refactorizar hacia patrones de diseño con IA

---

## Contexto

El flujo crítico `confirmar_y_pagar()` fue escrito durante el sprint inicial para cumplir con la historia HU-01. Al crecer el número de medios de pago (Yape, Culqi) y al agregar la función de IA para descripción de platos, el método alcanzó complejidad ciclomática 14 (clase C en radon), lo que dificulta las pruebas y hace que cada nuevo proveedor requiera modificar el servicio.

Problemas concretos detectados:
1. `if/elif` por medio de pago que crece con cada nuevo método.
2. El servicio conoce los detalles internos de cada SDK (interfaces distintas entre sí).
3. Bloque de reintentos duplicado para Yape y Culqi.
4. Condicionales anidados sobre `pedido.estado` (ignora la máquina de estados del Lab 05).
5. Las notificaciones WhatsApp se arman inline en el servicio.
6. La integración de IA mezcla lógica de proveedores con validaciones de salida.

---

## Decisión

Se aplican los siguientes patrones GoF al módulo `pedidos`:

| Olor | Patrón(es) | Archivo | Olor eliminado |
|------|-----------|---------|----------------|
| `if/elif` por medio de pago | **Strategy + Factory** | `pagos.py` | Agregar un nuevo medio ya no modifica el servicio |
| Detalles de SDK acoplados | **Adapter** | `pagos.py` | Cada SDK traduce a `PasarelaPago.cobrar()` |
| Reintentos duplicados | **Decorator** (`ConReintentos`) | `pagos.py` | Comportamiento transversal en un wrapper |
| Condicionales de estado | **State** | `estados.py` | Implementa `estados-pedido.mmd` del Lab 05 |
| Notificaciones manuales | **Observer** | `eventos.py` | Nuevos suscriptores sin tocar el servicio |
| IA mezclada | **Strategy + Adapter + Decorator + Chain of Responsibility** | `ia.py` | Proveedor LLM intercambiable; guardrails deterministas |

### Patrones rechazados

| Patrón propuesto | Razón del rechazo |
|-----------------|-------------------|
| **Singleton** para `FabricaPasarelas` | Introduce estado global e impide inyectar SDKs simulados en pruebas |
| **Abstract Factory** para familias de pasarelas | Solo hay 2 pasarelas; sería sobreingeniería ("patternitis") |
| **Proxy** para caché de menús | El caché vive en Redis (infraestructura); duplicarlo en el dominio viola SRP |
| **LLM como juez de guardrails** | Costo doble por llamada y latencia extra inaceptable para MVP de 1 mes |

---

## Consecuencias

### Positivas (+)
- `confirmar_y_pagar()` pasó de complejidad 14 (C) a 2 (A).
- Promedio de complejidad: de 5.5 (B) a 1.65 (A).
- Agregar Plin o transferencias solo requiere registrar un adaptador en la fábrica.
- 50 pruebas documentan el comportamiento; detectaron 1 error real de la IA (ConReintentos).
- La IA no puede inyectar precios o afirmaciones falsas en la descripción del plato.

### Negativas (−)
- SLOC creció de 112 a 328 y de 1 a 5 archivos.
- El equipo debe conocer los 7 patrones para mantener el código.
- La indirección puede sorprender a colaboradores nuevos.

### Error de la IA detectado por pruebas
La primera versión de `ConReintentos` generada por la IA capturaba `Exception` en lugar de `TimeoutError`, lo que causaba reintentos en pagos rechazados (riesgo de cobro duplicado). La prueba `test_con_reintentos_no_reintenta_pago_rechazado` falló y se corrigió manualmente.

---

## Alternativas consideradas

- **No refactorizar:** razonable si PicanteríaYa tuviera un solo medio de pago y nunca IA. Se descarta porque el negocio prevé agregar Plin y transferencias en sprints próximos.
- **Tabla de transiciones para State:** válida para máquinas sin comportamiento; descartada porque los estados de PicanteríaYa tienen acciones propias al entrar (encolar repartidor, activar GPS).
