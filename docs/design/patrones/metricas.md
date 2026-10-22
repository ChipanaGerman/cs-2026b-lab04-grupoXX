# Métricas y trade-off — E6 PicanteríaYa

> Herramienta: `radon` 6.x — `radon cc -s -a` y `radon raw -s`

## Complejidad ciclomática por método (McCabe)

### Antes del refactor (`antes/servicio.py`)

| Bloque | Complejidad | Calificación radon |
|--------|------------|-------------------|
| `ServicioPedidos.confirmar_y_pagar` | **14** | **C (riesgo alto)** |
| `ServicioPedidos.sugerir_descripcion_plato` | 7 | B |
| `ServicioPedidos` (clase) | 8 | B |
| `ServicioPedidos.__init__` | 5 | A |
| `ServicioPedidos.asignar_repartidor` | 4 | A |
| **Promedio general** | **5.5** | **B** |

### Después del refactor (todos los módulos con patrones)

| Módulo | Complejidad máxima | Promedio | Calificación |
|--------|--------------------|----------|--------------|
| `pagos.py` | 3 (`ConReintentos.cobrar`) | 1.55 | **A** |
| `estados.py` | 3 (`Recibido.registrar_pago`) | 1.55 | **A** |
| `eventos.py` | 3 (suscriptores) | 1.95 | **A** |
| `ia.py` | 4 (guardrails) | 1.70 | **A** |
| `servicio.py` | 2 (`confirmar_y_pagar`) | 1.67 | **A** |
| **Promedio total** | **4** | **1.65** | **A** |

### Resumen del cambio

| Métrica | Antes | Después | Cambio |
|---------|-------|---------|--------|
| Complejidad máxima | 14 (C) | 4 (A) | **−71 %** |
| Complejidad promedio | 5.5 (B) | 1.65 (A) | **−70 %** |
| SLOC (líneas de código real) | 112 | 328 | **+193 %** |
| Archivos | 1 | 5 | +4 archivos |
| Pruebas | 0 | 50 | +50 tests |

## Análisis del trade-off

**¿Qué ganamos?**
- `confirmar_y_pagar()` pasó de complejidad 14 (C, difícil de probar) a 2 (A, trivialmente verificable).
- Agregar un nuevo medio de pago (ej. Plin) ya no requiere tocar `ServicioPedidos`: solo registrar un `PlinAdapter` en la fábrica.
- La salida del LLM está aislada detrás de guardrails; una afirmación falsa de salud nunca llega al usuario.
- 50 pruebas documentan el comportamiento observable y detectaron 1 error real de la IA (ver E7 bitácora entrada 2).

**¿Qué costó?**
- El código creció de 112 a 328 SLOC y de 1 a 5 archivos.
- El equipo debe conocer los 7 patrones para mantener el código.
- La indirección extra puede sorprender a un colaborador nuevo.

**¿Cuándo la versión antes habría sido suficiente?**
Si PicanteríaYa fuera a tener **solo un medio de pago** (Yape) y **nunca integración de IA**, la versión antes era razonable. Los patrones se justifican por los **cambios previstos**: el negocio espera agregar Plin, transferencias y eventualmente Visa en los próximos sprints.

## Patrones que se decidió NO aplicar

| Patrón propuesto por la IA | Por qué se rechazó |
|----------------------------|--------------------|
| **Singleton** para `FabricaPasarelas` | Introduce estado global e impide inyectar SDKs simulados en las pruebas. La fábrica se inyecta normalmente. |
| **Abstract Factory** para "familias de pasarelas" | No existe una familia de productos relacionados; con 2 pasarelas sería sobreingeniería pura ("patternitis"). |
| **Proxy** para caché de menús | El caché de menús existe a nivel de infraestructura (Redis). Agregar un Proxy en el dominio duplicaría la responsabilidad. |
