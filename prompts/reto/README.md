# Reto adicional · Comparación de modelos

La opción A compara Qwen2.5 3B y Llama 3.2 3B mediante Ollama. Ambos reciben la v3.1 con el mismo dataset, temperatura 0, sin caché y con concurrencia 1. Ejecutar en el mismo equipo y registrar el identificador exacto de cada modelo (`ollama list`), el hardware y si el primer caso incluyó carga en frío.

```bash
ollama pull qwen2.5:3b
ollama pull llama3.2:3b
npx --yes promptfoo@0.118.0 eval -c prompts/reto/promptfooconfig.yaml --no-cache -j 1 -o reto-resultados.json
python prompts/reto/comparar.py reto-resultados.json
```

El costo de API es USD 0 para inferencia local. El costo de cómputo y energía requiere medición independiente. Conservar el JSON de Promptfoo como evidencia. La tasa y la latencia quedan pendientes hasta disponer de los dos modelos y ejecutar las llamadas.
