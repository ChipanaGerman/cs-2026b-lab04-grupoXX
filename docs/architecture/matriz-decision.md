# Matriz de decisión — PicanteríaYa

> **Contexto:** Delivery de picanterías arequipeñas. MVP en 1 mes, 3 developers, VPS único de bajo costo.  
> **Driver crítico:** Escalabilidad ante pico dominical de ×8 (hasta 400 pedidos/hora). Ver [drivers.md](drivers.md).

---

## Alternativas

- **A. Monolito en capas (n-tier):**  
  Un único despliegue organizado en capas clásicas (Presentación → Negocio → Datos). Toda la lógica reside en un proceso. Simple de desarrollar y desplegar, pero los módulos quedan acoplados entre sí. El escalado ante picos requiere replicar todo el proceso, no partes específicas.

- **B. Monolito modular + cola de mensajes (Redis/Celery):**  
  Un único despliegue dividido en módulos de dominio con interfaces explícitas (Menú, Pedidos, Pagos, Repartidores, Notificaciones). Las operaciones costosas (asignación de repartidor, notificaciones) se procesan de forma asíncrona mediante una cola Redis + workers Celery. El pico de pedidos se absorbe en la cola sin bloquear la API. Camino natural hacia microservicios si la carga lo exige en el futuro.

- **C. Microservicios:**  
  Cada dominio (Menú, Pedidos, Pagos, Repartidores, Notificaciones) se despliega como servicio independiente con su propia base de datos. Escalabilidad fina por servicio. Sin embargo, requiere API Gateway, orquestación, monitoreo distribuido y múltiples despliegues: complejidad operativa muy alta para 3 developers sin experiencia en DevOps y un plazo de 1 mes.

---

## Criterios y pesos (suman 100 %)

| Criterio                         | Peso | Justificación (driver relacionado)                                                                          |
|----------------------------------|------|-------------------------------------------------------------------------------------------------------------|
| Escalabilidad ante pico          | 30 % | QA-01: 400 pedidos/hora los domingos — es el driver crítico del caso; pesa más que cualquier otro criterio  |
| Tiempo de entrega del MVP        | 25 % | R-01: el MVP debe salir en 1 mes; una arquitectura compleja imposibilita cumplir el plazo                    |
| Costo operativo                  | 20 % | R-03: VPS único de bajo costo; múltiples servicios en nube disparan el gasto mensual                        |
| Modificabilidad                  | 15 % | RF-05, R-02: agregar picanterías, distritos o pasarelas de pago debe ser barato y seguro                    |
| Simplicidad operativa            | 10 % | R-02: 3 developers sin experiencia en DevOps; operar múltiples servicios aumenta el riesgo de caída         |

---

## Matriz (puntaje: 1 = muy malo … 5 = excelente)

| Criterio (peso)                  | A. Capas | B. Monolito modular + cola | C. Microservicios |
|----------------------------------|:--------:|:--------------------------:|:-----------------:|
| Escalabilidad ante pico (30 %)   |    2     |             4              |         5         |
| Tiempo de entrega MVP (25 %)     |    5     |             4              |         2         |
| Costo operativo (20 %)           |    5     |             5              |         2         |
| Modificabilidad (15 %)           |    2     |             4              |         5         |
| Simplicidad operativa (10 %)     |    5     |             4              |         1         |
| **Total ponderado**              | **3,55** |          **4,15**          |       **2,90**    |

**Cálculo:**
- A. Capas:    0,30×2 + 0,25×5 + 0,20×5 + 0,15×2 + 0,10×5 = 0,60+1,25+1,00+0,30+0,50 = **3,65**  *(corregido abajo)*
- B. Monolito: 0,30×4 + 0,25×4 + 0,20×5 + 0,15×4 + 0,10×4 = 1,20+1,00+1,00+0,60+0,40 = **4,20**
- C. Micro:    0,30×5 + 0,25×2 + 0,20×2 + 0,15×5 + 0,10×1 = 1,50+0,50+0,40+0,75+0,10 = **3,25**

> Ganador: **B — Monolito modular + cola de mensajes (4,20)**

---

## Afirmación de la IA que fue incorrecta

Durante la sesión con el asistente de IA (entrada 1 de la bitácora), la IA recomendó **microservicios con Kubernetes** argumentando que "el pico de ×8 requiere escalado independiente de cada servicio". El equipo verificó que:

1. **400 pedidos/hora = ~6–7 pedidos/minuto** — perfectamente manejable por un monolito con colas asíncronas.
2. Kubernetes requiere conocimientos de DevOps que el equipo no posee (R-02) y costos de nube elevados (R-03).
3. Yape **no tiene API pública abierta** — la IA asumió que sí y diseñó el microservicio de Pagos con integración directa. Se verificó en la documentación oficial de Yape y en foros de desarrollo peruano que la integración requiere un proveedor intermediario (Culqi o Niubiz).

La recomendación de la IA fue **rechazada**. El equipo eligió B conforme a los pesos y restricciones reales.

---

## Conclusión

Elegimos **B — Monolito modular + cola de mensajes** porque obtiene el mayor puntaje ponderado (4,20), es coherente con el plazo de 1 mes (R-01), el presupuesto bajo (R-03) y la experiencia del equipo (R-02). La cola Redis + workers Celery permite absorber el pico dominical de ×8 sin necesidad de múltiples despliegues. Los módulos con interfaces explícitas permiten extraerlos como microservicios en el futuro si la carga lo exige.

Ver decisión documentada en [ADR-001](adr/001-estilo-arquitectonico.md).
