# Reto adicional · Comparación de modelos

La opción A compara ERNIE 5.5 Flash Preview en Kilo con GPT-6 Luna en Duck.ai, sin credenciales ni descargas. Ambos recibieron los mismos ocho casos con el prompt v3.1. ERNIE usó temperatura 0 y hasta tres llamadas en paralelo. Luna usó el modo Rápido, un chat nuevo por caso y ejecución secuencial. Liquid se sustituyó por Luna cuando Kilo agotó su cuota anónima.

```bash
npx --yes promptfoo@0.118.0 eval -c prompts/reto/promptfooconfig.yaml --no-cache -j 1 -o prompts/evidencia/reto.json
python prompts/reto/comparar.py prompts/evidencia/reto.json
```

Promptfoo evalúa el texto de las capturas. El costo de ERNIE proviene de `usage.cost`. Para Luna se registra el costo directo del acceso web gratuito. Las latencias incluyen el tiempo de la solicitud a Kilo o el tiempo desde el envío hasta que Duck.ai mostró la respuesta completa. La concurrencia y el canal difieren, por lo que estos tiempos describen la experiencia observada y no aíslan la velocidad de cada modelo.

| Modelo | Aprobación | Mediana | Costo medio de API |
| --- | ---: | ---: | ---: |
| ERNIE 5.5 Flash Preview | 8/8 | 5.901 ms | USD 0 por caso |
| GPT-6 Luna | 8/8 | 4.085 ms | USD 0 por caso en Duck.ai |

La revisión manual encontró que Luna nombró a Yape como actor en H4, H5 y H8. Las aserciones de esquema y vocabulario no penalizan esa sustitución. El resultado automático mide los criterios cubiertos por las aserciones.
