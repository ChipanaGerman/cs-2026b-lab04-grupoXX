# Backlog de PicanteríaYa para el Laboratorio 9

Este archivo es el Product Backlog de PicanteríaYa para el alcance del Lab 09. Las seis historias quedan registradas en el repositorio. H7 y H8 pertenecen al dataset de evaluación.

| Historia | Caso | Como | Quiero | Para | Aceptación |
| --- | --- | --- | --- | --- | --- |
| HU-01 | H1 | Cliente | Confirmar mi pedido y pagar con Yape | Almorzar sin usar efectivo | Ver pedido pagado si se aprueba o cancelado con el motivo si se rechaza. |
| HU-02 | H2 | Cliente | Consultar el menú del día | Elegir mi almuerzo | Ver los nombres de los platos publicados o un aviso de que el menú aún no está disponible. |
| HU-03 | H3 | Cliente | Saber qué plato se agotó al confirmar | Evitar pagar por un plato que ya no está disponible | Pasar al pago con todos los platos disponibles. Si uno se agota, ver su nombre y que el pago quede sin procesar. |
| HU-04 | H4 | Cliente | Saber si se asignó un repartidor | Conocer el avance de mi pedido pagado | Ver que se asignó un repartidor si hay disponibilidad o que la asignación sigue pendiente. |
| HU-05 | H5 | Cliente | Seguir el reparto en el mapa | Saber dónde está mi pedido | Ver la posición actualizada si hay señal o la última posición con un aviso si se pierde. |
| HU-06 | H6 | Cliente | Conocer el resultado del pago pendiente | Saber si debo volver a pedir | Ver el pedido pagado si se aprueba antes de diez minutos o ver la cancelación y su motivo al cumplirse el plazo sin respuesta. |

## Orden inicial y fuentes

El orden inicial sigue el recorrido del cliente, desde consultar el menú hasta seguir el reparto. El equipo puede reordenar las historias durante el refinamiento. La incorporación al backlog registra el trabajo del producto y no implica que se haya desarrollado o asignado a un sprint.

| Orden | Historia | Estado inicial | Fuente |
| ---: | --- | --- | --- |
| 1 | HU-02 | Por refinar | [Descripción del caso](../../README.md#caso) |
| 2 | HU-03 | Por refinar | [HU-01, escenario de stock insuficiente](../../docs/design/historia.md) |
| 3 | HU-01 | Definida | [Historia y criterios originales](../../docs/design/historia.md) |
| 4 | HU-06 | Por refinar | [HU-01, escenario de pago rechazado o sin respuesta](../../docs/design/historia.md) |
| 5 | HU-04 | Por refinar | [Flujo de asignación de repartidor](../../docs/design/actividades-asignacion-repartidor.puml) |
| 6 | HU-05 | Por refinar | [Seguimiento en tiempo real](../../docs/architecture/adr/003-comunicacion-tiempo-real.md) |

HU-01 procede del diseño previo. HU-02 a HU-06 se formalizaron a partir del diseño al organizar el backlog del laboratorio. Los identificadores H1 a H6 permiten rastrear cada historia al [dataset de Promptfoo](casos.yaml).
