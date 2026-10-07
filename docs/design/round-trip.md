# Round-trip: Diagrama de diseño ↔ Código Python

> **E6 — PicanteríaYa | Módulo: pedidos**
>
> Herramienta de ingeniería inversa usada: `pyreverse` (pylint)
>
> Comando ejecutado:
> ```bash
> pip install pylint
> pyreverse -o puml -p pedidos src/pedidos
> java -jar plantuml.jar -tpng classes_pedidos.puml
> ```

---

## Tabla de diferencias: diagrama de diseño vs. diagrama obtenido del código

| # | Diferencia observada | Causa | Acción tomada |
|---|----------------------|-------|---------------|
| 1 | La composición `Pedido *── LineaPedido` no aparece en el diagrama inverso; `lineas` figura como un atributo de tipo `list[LineaPedido]`. | `pyreverse` no infiere relaciones de composición a partir de colecciones tipadas; solo lee el tipo del atributo. | **Ninguna**: limitación documentada de la herramienta. El diagrama de diseño se mantiene con la composición, pues refleja la regla del negocio (las líneas no existen sin el pedido). |
| 2 | No aparecen multiplicidades en ninguna relación del diagrama inverso. | Python no tiene un mecanismo de anotación de multiplicidades que `pyreverse` pueda leer; los tipos `List[X]` no distinguen `0..*` de `1..*`. | **Corrección en el código**: se agregó validación `if not self.lineas: raise ValueError(...)` en `confirmar()` para forzar la multiplicidad `1..*` (regla C3). |
| 3 | `PasarelaPago`, `RepositorioPedidos`, `ColaMensajes` y `Notificador` aparecen como clases ordinarias en lugar de interfaces (estereotipo `<<puerto>>`). | Python implementa interfaces con `ABC` y `@abstractmethod`; `pyreverse` las muestra como clases concretas. | **Aceptable**: se documenta la equivalencia en este archivo. Los estereotipos `<<puerto>>` y `<<adaptador>>` se mantienen solo en el diagrama de diseño. |
| 4 | `CulqiYapeAdapter` y `CeleryColaMensajesAdapter` aparecen sin atributos ni métodos visibles (solo el método `cobrar` / `encolar_asignacion_repartidor` figura como abstracto heredado). | Los adaptadores solo tienen métodos heredados que lanzan `NotImplementedError`; `pyreverse` los muestra vacíos. | **Aceptable para el MVP**: los adaptadores son stubs hasta integrar con Culqi y Celery. Se registra en la bitácora de IA. |
| 5 | Los nombres de métodos en el código usan `snake_case` (p. ej. `calcular_total`, `registrar_pago`) mientras que el diagrama UML usa `camelCase` (`calcularTotal`, `registrarPago`). | Convención de Python (PEP 8) vs. convención UML. | **Documentar equivalencia (C5)**: se acepta la diferencia de convención y se agrega nota en el diagrama: `' PEP 8: calcular_total`. Los nombres del dominio son los mismos en ambos lenguajes. |

---

## Observaciones adicionales

- `Repartidor` y su relación con `Pedido` no aparecen en `classes_pedidos.puml` porque están en el módulo `repartidores`, separado por diseño (ADR-001 — sin imports cruzados directos).
- La relación `Pedido → Pago` (0..1) se infiere correctamente por `pyreverse` como atributo opcional `pago: Optional[Pago]`.
