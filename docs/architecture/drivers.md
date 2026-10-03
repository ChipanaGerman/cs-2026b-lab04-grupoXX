# Drivers arquitectónicos — PicanteríaYa

> **Caso:** Delivery de picanterías arequipeñas  
> **Actores principales:** Cliente, Picantería, Repartidor  
> **Atributo crítico:** Escalabilidad — los pedidos se multiplican por 8 los domingos de 12:00 a 15:00 (hasta 400 pedidos/hora)

---

## 1. Requisitos funcionales clave

| ID    | Requisito                                                                                  | Actor            | Prioridad |
|-------|--------------------------------------------------------------------------------------------|------------------|-----------|
| RF-01 | El cliente visualiza el menú del día de cada picantería disponible, filtrado por distrito  | Cliente          | Alta      |
| RF-02 | El cliente selecciona platos, realiza un pedido y paga con Yape a través de la plataforma  | Cliente          | Alta      |
| RF-03 | El sistema asigna automáticamente un repartidor disponible al pedido confirmado            | Sistema          | Alta      |
| RF-04 | El cliente realiza seguimiento en tiempo real de la ubicación del repartidor en el mapa    | Cliente          | Alta      |
| RF-05 | La picantería publica, actualiza y desactiva el menú del día y su stock disponible         | Picantería       | Alta      |
| RF-06 | El repartidor recibe notificación del pedido asignado y actualiza su posición GPS          | Repartidor       | Alta      |
| RF-07 | El sistema notifica al cliente y a la picantería sobre el estado del pedido (confirmado, en camino, entregado) | Sistema | Media |
| RF-08 | El cliente puede calificar el pedido y al repartidor al finalizar la entrega               | Cliente          | Baja      |

---

## 2. Atributos de calidad (ordenados por prioridad)

1. **Escalabilidad** — El sistema debe soportar picos de carga de hasta 400 pedidos/hora los domingos de 12:00 a 15:00, representando un incremento de ×8 respecto al flujo normal (~50 pedidos/hora). La arquitectura debe permitir absorber este pico sin rediseño.

2. **Rendimiento** — El tiempo de respuesta de las operaciones principales (consultar menú, confirmar pedido) debe ser bajo incluso durante horas pico, para no perder ventas por espera.

3. **Disponibilidad** — El servicio debe estar operativo especialmente en los horarios de alta demanda (domingos 12:00–15:00). Una caída durante el pico implica pérdida directa de ingresos para las picanterías.

4. **Modificabilidad** — El sistema debe permitir incorporar nuevas picanterías, nuevos distritos de reparto o nuevas pasarelas de pago con mínimo impacto en los módulos existentes.

5. **Seguridad** — Los datos de pago (transacciones Yape), la ubicación GPS de repartidores y los datos personales de clientes deben protegerse conforme a la Ley 29733.

---

## 3. Restricciones

| ID   | Tipo         | Restricción                                                                                                     |
|------|--------------|-----------------------------------------------------------------------------------------------------------------|
| R-01 | Plazo        | El MVP debe estar en producción en **1 mes** a partir del inicio del proyecto                                   |
| R-02 | Equipo       | 3 developers con experiencia en Python/Django, JavaScript y bases de datos relacionales; sin experiencia en DevOps avanzado |
| R-03 | Presupuesto  | Bajo; se utilizará un único VPS en la nube (ej. DigitalOcean/Linode ~$20/mes). No se pueden costear múltiples servicios gestionados |
| R-04 | Normativa    | Ley 29733 de protección de datos personales (Perú): datos de clientes y repartidores requieren consentimiento y almacenamiento seguro |
| R-05 | Tecnología   | La integración con Yape **no dispone de API pública abierta**: requiere un proveedor de pagos intermediario (ej. Culqi, Niubiz) o convenio directo |
| R-06 | Dependencia  | Google Maps API tiene costos variables; se debe controlar el uso para no exceder el nivel gratuito en etapa MVP  |

---

## 4. Escenarios de atributos de calidad

| ID    | Atributo       | Fuente                        | Estímulo                                                         | Entorno                                          | Artefacto                  | Respuesta                                                             | Medida                                                    |
|-------|----------------|-------------------------------|------------------------------------------------------------------|--------------------------------------------------|----------------------------|-----------------------------------------------------------------------|-----------------------------------------------------------|
| QA-01 | Escalabilidad  | 400 clientes distintos        | Realizan pedidos simultáneos a diferentes picanterías            | Domingo 12:00–15:00, pico máximo de demanda      | Módulo de Pedidos + API    | El sistema acepta, encola y procesa todos los pedidos sin rechazar ninguno | p95 del tiempo de confirmación ≤ 4 s; 0 pedidos perdidos o rechazados por sobrecarga |
| QA-02 | Rendimiento    | 1 cliente                     | Consulta el menú del día de una picantería                       | Operación normal (~50 pedidos/hora), red 4G      | Módulo Menú / API REST     | Devuelve la lista de platos disponibles con precios                  | p95 del tiempo de respuesta ≤ 1 s                         |
| QA-03 | Disponibilidad | Monitor de salud (health check) | Detecta falla en el proceso de aplicación principal             | Domingo 13:00 h, pico activo                     | Servidor de aplicación     | El supervisor reinicia el proceso automáticamente sin pérdida de pedidos en vuelo | Tiempo de recuperación ≤ 30 s; disponibilidad ≥ 99.5 % en horario pico |
| QA-04 | Modificabilidad | Developer del equipo          | Necesita incorporar un nuevo distrito de reparto al sistema      | Entorno de desarrollo, sin presión de producción | Módulo de Repartidores     | El cambio se realiza sin modificar otros módulos                     | Esfuerzo ≤ 1 día-persona; 0 módulos ajenos modificados    |
