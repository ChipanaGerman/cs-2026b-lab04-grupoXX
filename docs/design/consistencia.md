# Revisión de consistencia — PicanteríaYa

> **E7** | Aplicado el Prompt IA 3 (auditor de consistencia) sobre los cinco diagramas del Lab 05.
> Reglas verificadas: C1–C5 (ver Tabla 2 de la guía).

---

## Tabla de hallazgos

| Regla | Elemento / Línea | Hallazgo de la IA | Verificación del equipo | Estado |
|-------|-----------------|-------------------|-------------------------|--------|
| C1 | `secuencia-pedir-pagar.puml`, mensaje `encolarAsignacionRepartidor(pedidoId)` | "El mensaje `encolarAsignacionRepartidor` se envía a `ColaMensajes`, pero esta interfaz no aparece en el diagrama de clases como clase con esa operación." | **Verdadero positivo**: se verificó y confirmó. La operación `encolar_asignacion_repartidor` estaba en el código Python pero faltaba en `clases.puml`. Se agregó la interfaz `ColaMensajes <<puerto>>` al diagrama de clases. | ✅ Corregido |
| C2 | `estados-pedido.mmd`, transición `PAGADO → PREPARANDO` | "La transición 'repartidor asignado' no corresponde a ninguna operación de la clase `Pedido`." | **Verdadero positivo**: la transición se renombró a `marcarPreparando()` que sí es una operación de `Pedido` (ver `clases.puml` y `dominio.py`). | ✅ Corregido |
| C3 | `clases.puml`, relación `Pedido *── LineaPedido` | "La multiplicidad `1..*` en `LineaPedido` no se valida en el código; el pedido podría tener cero líneas." | **Verdadero positivo**: se agregó validación `if not self.lineas: raise ValueError(...)` en `Pedido.confirmar()`. | ✅ Corregido |
| C4 | `paquetes.puml`, dependencia `REP ..> NOT` | "El paquete `repartidores` depende de `notificaciones` y también `pedidos` depende de `notificaciones`; esto podría crear un ciclo indirecto `pedidos → repartidores → notificaciones → pedidos`." | **Falso positivo**: la IA confundió una dependencia en cadena con un ciclo. El ciclo real sería `pedidos → notificaciones → pedidos`, pero `notificaciones` NO depende de `pedidos`. El flujo es unidireccional: `pedidos` y `repartidores` usan el puerto `Notificador`, pero `notificaciones` no importa ni conoce a ninguno de ellos. Se rechaza el hallazgo. | ❌ Rechazado (falso positivo) |
| C5 | Todos los diagramas | "Los métodos en el código Python usan `snake_case` (`calcular_total`, `registrar_pago`) mientras que los diagramas UML usan `camelCase` (`calcularTotal`, `registrarPago`): inconsistencia de nombres." | **Parcialmente válido**: la diferencia es de convención de lenguaje (PEP 8 vs. UML), no de dominio. Los nombres del negocio son idénticos. Se agrega una nota en `clases.puml` documentando la equivalencia y se considera aceptable (igual que el ejercicio resuelto del docente). | ⚠️ Documentado |

---

## Notas sobre el falso positivo (regla C4)

La IA identificó un supuesto ciclo `pedidos → repartidores → notificaciones → pedidos`, pero este análisis es incorrecto porque:

1. `notificaciones` implementa el puerto `Notificador` (un adaptador), pero **no importa ni conoce** el módulo `pedidos` ni `repartidores`.
2. La dependencia declarada en `paquetes.puml` es `PED ..> NOT` y `REP ..> NOT`, ambas unidireccionales hacia `notificaciones`.
3. Si hubiera un ciclo real, se resolvería introduciendo un evento/puerto intermedio; pero en este caso no es necesario.

**Lección aprendida**: la IA tiende a confundir cadenas de dependencias largas con ciclos. Siempre se debe verificar la dirección de cada flecha antes de aceptar un hallazgo de C4.
