# Comparación de herramientas: Structurizr DSL vs. C4-PlantUML escrito a mano

> **E6 — Lab 06** | Comparación entre el enfoque de modelado (workspace.dsl) y el de diagramación (contexto-manual.puml).

---

## 1. Comparación directa

| Criterio | Structurizr DSL (workspace.dsl) | C4-PlantUML escrito a mano (contexto-manual.puml) |
|----------|---------------------------------|---------------------------------------------------|
| **Tiempo de creación** | ~40 min (modelo completo con 5 vistas) | ~8 min (solo el diagrama de contexto) |
| **Número de archivos** | 1 archivo → 5 vistas exportadas automáticamente | 1 archivo por cada diagrama que se quiera |
| **Consistencia entre vistas** | Garantizada: si se cambia el nombre de un contenedor en el DSL, todas las vistas se actualizan al re-exportar | Manual: habría que editar todos los `.puml` donde aparezca ese contenedor |
| **Errores encontrados al escribir** | El validador (`structurizr validate`) detecta identificadores inexistentes y relaciones a elementos no definidos antes de exportar | El error solo aparece al renderizar con PlantUML; sin validación semántica |
| **Curva de aprendizaje** | Mayor: requiere conocer la sintaxis DSL, los bloques `model` y `views`, y las restricciones de `!identifiers hierarchical` | Menor: el formato es una extensión directa de PlantUML con macros C4 |
| **Renderizado en GitHub** | No nativo; necesita exportar a Mermaid y embeber en el README | No nativo; requiere servidor PlantUML o extensión VS Code |
| **Vista dinámica y de despliegue** | Integradas en el mismo modelo; se derivan automáticamente | Requieren archivos separados escritos a mano |

---

## 2. Escenario de cambio de nombre

**Pregunta:** ¿Qué pasaría si mañana cambia el nombre del contenedor `App Cliente / PWA` a `Portal Cliente`?

- **Con Structurizr DSL:** se edita **una sola línea** en `workspace.dsl` (`pwa = container "Portal Cliente" ...`). Al re-exportar con la CLI, las cinco vistas (contexto, contenedores, componentes, dinámica y despliegue) reflejan automáticamente el nuevo nombre. El `validate` garantiza que no quedó ninguna referencia huérfana.

- **Con C4-PlantUML escrito a mano:** habría que buscar y reemplazar `"App Cliente / PWA"` en **cada archivo** que lo mencione (contexto-manual.puml, contenedores.puml, despliegue.puml, etc.). Es fácil olvidar uno y crear inconsistencias que el renderizador no detecta.

---

## 3. Vista dinámica C4 vs. diagrama de secuencia UML (Lab 05)

La **vista dinámica** (`dynamic` en workspace.dsl) muestra 8 pasos numerados entre componentes de la API para el flujo "Pedir y pagar con Yape". Es un resumen de alto nivel útil para **comunicar el flujo a arquitectos y gerentes de proyecto**.

El **diagrama de secuencia UML** (`secuencia-pedir-pagar.puml`, Lab 05) muestra el mismo flujo con 29 mensajes detallados, incluyendo:
- Fragmentos `loop` por cada línea del pedido
- Fragmento `alt` para pago aprobado vs. rechazado
- Mensajes asíncronos (`->>`) hacia la cola y el notificador
- Tipos de retorno y notas de comportamiento

La secuencia UML está dirigida a **developers** que implementarán el código. La vista dinámica C4 está dirigida a **todos los stakeholders técnicos** que necesitan entender el flujo sin el detalle de implementación.

---

## 4. Conclusión

Para un MVP de 1 mes con un equipo de 3 personas, el enfoque **Structurizr DSL es superior** porque garantiza la consistencia de todo el modelo con un solo artefacto. El esfuerzo inicial de aprendizaje se amortiza en la primera vez que cambia un contenedor o se agrega una vista. El `contexto-manual.puml` es útil como ejercicio didáctico o para compartir un diagrama puntual sin levantar la CLI.
