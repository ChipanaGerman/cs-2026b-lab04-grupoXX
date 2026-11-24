# E1. Lienzo de PicanteríaYa

| Decisión | Elección | Justificación |
|---|---|---|
| Agente o flujo | Agente para explorar y corregir; flujo fijo para validar y probar | La ubicación de la causa requiere inspección; cobrar y validar cantidad deben ser deterministas (sección 1.1). |
| Arquetipo | ReAct en issues 1 y 3; planificador-ejecutor con reflexión en issue 2 | ReAct permite buscar y observar errores. El problema de cantidades tiene casos límite que justifican crítica (1.3). |
| Herramientas | Leer, buscar, editar fragmento único, probar, diff; mapa AST y notas | Interfaces pequeñas, sin shell libre ni red. Tests son de solo lectura (1.5). |
| Memoria | Historial de tarea y notas persistentes por sandbox | Hipótesis sobre disponibilidad y archivos revisados; no compartir notas entre experimentos (1.6). |
| Coordinación | Único como base; gestor y actor-crítico como comparación | Especialización con mínimo privilegio; solo conservar más agentes si sus hallazgos compensan costo (1.7). |
| Rol humano | Revisor de cada edición y del PR | Confianza inicial baja; solo una persona del grupo puede aceptar el cambio (1.8). |
| Control | Contrato estricto, rutas resueltas, 12 pasos por actor, 8 crítico, 2 rondas | También las decisiones inválidas consumen presupuesto. Sin credenciales ni ejecución en main. |

Issues reales del esqueleto `src/pedidos/dominio.py`: delivery omitido,
cantidad inválida aceptada y repartidor ocupado reasignado. La comparación
usa copias independientes de la misma base y pruebas inmutables.
