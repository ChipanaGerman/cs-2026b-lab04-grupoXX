# Lab 09 · Cuestionario y entrega

1. Un prompt especifica qué datos recibe la tarea, qué decisión toma y qué salida entrega. Como una historia ambigua, una instrucción como «escribe buenos criterios» admite resultados incompatibles entre sí.
2. v2 agrega rol, contexto, decisión INVEST y formato. v3 añade un ejemplo y un límite de confianza, y v3.1 explicita la defensa ante documentos citados. Las hipótesis corresponden a las aserciones de esquema, INVEST, cobertura e integridad. La magnitud de las mejoras se determinará con grabaciones.
3. El objeto JSON permite validar claves, tipos y relaciones entre campos antes de consumirlo. El contrato de Conventional Commits es un esquema de cadena para conservar directamente el encabezado.
4. Few-shot enseña con ejemplos de entrada y salida. Chain-of-thought solicita razonamiento intermedio. Añadir una explicación visible rompe el contrato de JSON puro.
5. Una tasa del 100 % mide el dataset y sus aserciones. El chequeo de palabras en H6, por ejemplo, puede encontrar «10» aunque el texto invierta la condición de cancelación. La revisión semántica sigue siendo necesaria.
6. En H7, buscar «Redis» en todo el JSON marcaría como incorrecta la pregunta «¿Qué resultado debe mejorar tras sustituir Redis?». La aserción se limita a los escenarios, donde se requiere comportamiento observable.
7. La inyección directa ordena imprimir un marcador dentro de una historia. La indirecta lo ordena dentro de una nota citada. PicanteríaYa delimita y serializa los datos, instruye al modelo para que los trate como datos, limita el generador a texto, valida el esquema y busca marcadores en los ensayos locales.
8. Las tres rondas con GPT-6 Luna mantuvieron la decisión INVEST y aprobaron las seis aserciones, con diferencias de redacción y del actor descrito en H8. Las grabaciones permiten reproducir las pruebas y las llamadas nuevas permiten observar esas variaciones. Véase la [bitácora](bitacora-ia.md).

## Revisión y cierre

- En la clínica, solicitar la v1 del grupo asignado, evaluar una entrada autorizada y abrir un issue en su repositorio con el cambio propuesto y el caso que lo justifica.
- Cada integrante debe abrir desde su cuenta un PR para una versión de prompt. En la rama de su versión, incluir el diff, el caso que falló, las grabaciones y el informe de Promptfoo. En PR encadenados, establecer como base la rama que contiene la versión anterior.
- El integrante revisor abre **Files changed → Review changes**, coteja los cinco puntos de la guía y registra una revisión real. Confirmar el estado de **Prompts Lab 09** en **Checks** antes de fusionar.
- Tras fusionar los PR y verificar las evaluaciones, actualizar la rama principal y ejecutar `git tag -a v0.9-prompts -m "Entrega Lab 09"` y `git push origin v0.9-prompts`. Entregar el enlace del repositorio en el Aula Virtual.
