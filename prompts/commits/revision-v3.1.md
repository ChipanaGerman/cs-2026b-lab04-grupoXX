# Revisión de Conventional Commits v3.1

El [caso C7](casos.yaml) cambia la visibilidad de un plato de siempre visible a visible solo con stock. La regla añadida a [v3.1](v3.1.txt) clasifica como `fix` un cambio que evita mostrar algo inválido bajo una regla de disponibilidad.

| Versión | Modelo | Resultado de C7 | Total |
| --- | --- | --- | ---: |
| v3 | ERNIE 5.5 Flash Preview | [`feat(menu)`](grabaciones/v3/C7.txt) | 7/8 |
| v3.1 | GPT-6 Luna | [`fix(menu): oculta platos sin stock`](grabaciones/v3.1/C7.txt) | 8/8 |

El [informe de Promptfoo](../evidencia/commits.json) registra la comprobación de tipo, ámbito, esquema, fidelidad e integridad. El resultado de v3.1 resuelve C7 en la muestra observada. Una comparación con un mismo modelo permitiría medir el efecto de la regla por separado.
