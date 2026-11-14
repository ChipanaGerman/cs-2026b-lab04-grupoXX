# Reto adicional · Comparación de modelos

La opción A usa dos modelos alojados de Kilo sin credenciales ni descargas, ERNIE 5.5 Flash Preview y Liquid LFM 3 1.7B. Ambos reciben la v3.1 con el mismo dataset y temperatura 0. La latencia registrada es el tiempo de la solicitud de inferencia completa. Las capturas de ERNIE se reutilizaron de la evaluación principal, que utilizó hasta tres llamadas en paralelo. Esta diferencia de concurrencia puede afectar la comparación.

```bash
python prompts/capturar_kilo.py reto
npx --yes promptfoo@0.118.0 eval -c prompts/reto/promptfooconfig.yaml --no-cache -j 1 -o prompts/evidencia/reto.json
python prompts/reto/comparar.py prompts/evidencia/reto.json
```

El costo proviene del campo `usage.cost` de Kilo. Promptfoo evalúa el texto capturado y el comparador toma la latencia de los metadatos de inferencia. Kilo devolvió HTTP 429 `PROMOTION_MODEL_LIMIT_REACHED` al ejecutar Liquid sobre el dataset. Queda pendiente completar la comparación cuando el proveedor vuelva a admitir llamadas anónimas.

| Modelo | Aprobación | Mediana | Costo medio de API |
| --- | ---: | ---: | ---: |
| ERNIE 5.5 Flash Preview | 8/8 | 5.901 ms | USD 0 por caso |
| Liquid LFM 3 1.7B | Sin capturas evaluables | Pendiente | Pendiente |
