# Historia de usuario — PicanteríaYa

## HU-01: Pedir el menú del día y pagar con Yape

**Como** cliente,  
**quiero** ver el menú del día de una picantería disponible en mi distrito, seleccionar platos y pagar con Yape a través de la plataforma,  
**para** realizar mi pedido de almuerzo de forma rápida y sin efectivo.

---

## Criterios de aceptación

**CA-01 — Pedido exitoso con pago aprobado**

- **Dado** un cliente autenticado que visualiza el menú del día de una picantería con stock disponible,
- **Cuando** selecciona uno o más platos, confirma el pedido y el pago con Yape es aprobado por el proveedor intermediario (Culqi),
- **Entonces** el pedido queda en estado **PAGADO**, el sistema encola la asignación del repartidor más cercano disponible, y el cliente recibe una notificación de confirmación.

**CA-02 — Pago rechazado o sin respuesta**

- **Dado** un cliente con un pedido confirmado y en espera de pago,
- **Cuando** el pago con Yape es rechazado por el proveedor o no hay respuesta en 10 minutos,
- **Entonces** el pedido queda en estado **CANCELADO**, el stock reservado se libera y el cliente recibe un aviso del motivo.

**CA-03 — Stock insuficiente**

- **Dado** un cliente que intenta confirmar un pedido,
- **Cuando** uno o más platos del pedido ya no tienen stock disponible en la picantería,
- **Entonces** el sistema notifica al cliente los platos sin stock y no procesa el pago.

---

## Notas técnicas

- El pago con Yape se canaliza a través de **Culqi** (intermediario, restricción R-05 del ADR-001).
- La asignación de repartidor es **asíncrona**: se encola en Redis/Celery al confirmar el pago.
- Los módulos involucrados: **Menú**, **Pedidos**, **Pagos**, **Repartidores**, **Notificaciones** (ADR-001).
