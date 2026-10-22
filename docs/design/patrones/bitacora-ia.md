# Bitácora de IA — Lab 07 Patrones de Diseño · PicanteríaYa

> Regla de oro: la IA propone, el equipo decide y verifica.
> Ningún patrón entra al código sin: (1) un olor concreto, (2) pruebas en verde antes y después, (3) una métrica que muestre la mejora y (4) un registro aquí.

---

## Interacción 1 — Detector de olores (Prompt IA 1)

**Prompt (resumen):**
> Actúa como revisor de código experto en refactorización (Fowler) y patrones GoF. Contexto: [antes/servicio.py + salida de radon]. Tarea: identifica los olores de código. Para cada uno indica: líneas, olor, patrón GoF propuesto, principio SOLID y costo de aplicarlo. No escribas código todavía; no propongas patrones sin un olor concreto; no uses Singleton. Formato: tabla Markdown.

**Propuesta de la IA:**
- 6 olores con patrones: Strategy+Factory (if/elif medio pago), Adapter (detalles SDK), Decorator (reintentos duplicados), State (condicionales de estado), Observer (notificaciones manuales), Strategy+Adapter+Chain (IA mezclada)
- 2 propuestas extra: Singleton para `FabricaPasarelas`, Abstract Factory para "familias de pasarelas"

**Verificación del equipo:**
- Revisado contra `antes/servicio.py` línea por línea
- Confirmado que `confirmar_y_pagar()` tiene complejidad 14 (radon lo clasifica C)

**Decisión:**
- ✅ 6 patrones aceptados — eliminan olores concretos medibles
- ❌ Singleton rechazado — introduce estado global e impide inyectar SDKs en pruebas
- ❌ Abstract Factory rechazado — solo hay 2 pasarelas; es sobreingeniería ("patternitis")

---

## Interacción 2 — Error detectado por las pruebas: ConReintentos

**Prompt (resumen):**
> Aplica ÚNICAMENTE el patrón Decorator (ConReintentos) al bloque de reintentos del siguiente código [pegar antes/servicio.py]. No cambies el comportamiento observable; las pruebas deben seguir pasando; no uses Singleton ni estado global.

**Propuesta de la IA:**
```python
# Primera versión de la IA (incorrecta)
def cobrar(self, monto, celular):
    for _ in range(self._intentos):
        try:
            return self._interna.cobrar(monto, celular)
        except Exception:  # ← demasiado amplio
            continue
    return ResultadoPago(False)
```

**Verificación:**
- `test_con_reintentos_no_reintenta_pago_rechazado` **FALLÓ** con la versión de la IA
- El problema: capturaba `Exception` en lugar de solo `TimeoutError`, por lo que reintentaba también los pagos rechazados (podría generar cobros duplicados en producción)

**Decisión:**
- ❌ Versión de la IA **rechazada** y corregida manualmente
- ✅ Versión final solo captura `TimeoutError`; la prueba pasó
- Esta fue la corrección más importante del laboratorio

---

## Interacción 3 — Propuesta de State con diccionario de transiciones

**Prompt (resumen):**
> Implementa el patrón State para el ciclo de vida del pedido usando la tabla de transiciones del archivo estados-pedido.mmd del Lab 05.

**Propuesta de la IA:**
Sugirió una implementación con un diccionario de transiciones:
```python
TRANSICIONES = {
    "RECIBIDO": {"registrar_pago": "PAGADO", "cancelar": "CANCELADO"},
    ...
}
```

**Verificación:**
- La propuesta es válida para máquinas de estado simples
- Sin embargo, los estados de PicanteríaYa tienen **comportamiento propio**: al entrar a PAGADO se encola la asignación del repartidor; al entrar a EN_CAMINO se activa el GPS

**Decisión:**
- ❌ Propuesta con diccionario **rechazada** — no soporta comportamiento en las transiciones
- ✅ Se implementó el patrón State completo con clase base + subclases concretas

---

## Interacción 4 — Guardrails de IA con LLM como juez

**Prompt (resumen):**
> Para validar la salida del LLM en la descripción del plato, ¿conviene usar otro modelo de lenguaje como juez en lugar de reglas deterministas?

**Propuesta de la IA:**
Sugirió usar un LLM secundario para evaluar si la respuesta tiene precios o afirmaciones falsas, argumentando mayor flexibilidad.

**Verificación:**
- Costo adicional por llamada (doble o triple)
- Latencia extra (segunda llamada a la API)
- Para un MVP de 1 mes, el riesgo de un LLM-juez que también se equivoque es inaceptable

**Decisión:**
- ❌ Propuesta **rechazada**
- ✅ Se implementó cadena de guardrails con reglas deterministas (SinPrecios, SinAfirmacionesProhibidas, LongitudMaxima)

---

## Interacción 5 — Diagramas PlantUML desde el código

**Prompt (resumen):**
> Genera los diagramas de clases PlantUML de los módulos pagos.py, estados.py, eventos.py e ia.py con los estereotipos de rol (<<Strategy>>, <<Adapter>>, etc.).

**Propuesta de la IA:**
Generó 4 diagramas con estereotipos, relaciones y notas explicativas.

**Verificación:**
- Comparado con el código real: los nombres de clases, métodos y relaciones eran correctos
- Dos correcciones menores: `ConSeguimientoGPS` aparecía sin estereotipo `<<Decorator>>` y faltaba la relación `ConCache o-- ProveedorLLM`

**Decisión:**
- ✅ Diagramas aceptados con 2 correcciones de nombres y relaciones aplicadas manualmente
