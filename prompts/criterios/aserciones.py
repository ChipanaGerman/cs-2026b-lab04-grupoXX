"""Aserciones deterministas independientes para criterios de aceptación."""

import json
import re
from pathlib import Path

from jsonschema import Draft202012Validator

VALIDADOR = Draft202012Validator(
    json.loads(Path(__file__).with_name("esquema.json").read_text(encoding="utf-8"))
)


def objeto(output):
    try:
        valor = json.loads(output)
    except (TypeError, ValueError):
        return {}
    return valor if isinstance(valor, dict) else {}


def esquema(output, context):
    return VALIDADOR.is_valid(objeto(output))


def identidad(output, context):
    return objeto(output).get("historia_id") == context["vars"]["id"]


def invest(output, context):
    return objeto(output).get("invest_ok") is context["vars"]["invest_ok"]


def texto_escenarios(output):
    return json.dumps(objeto(output).get("escenarios", []), ensure_ascii=False)


def observable(output, context):
    # Las preguntas al PO pueden citar el término técnico de una historia no INVEST.
    return not re.search(
        r"\b(?:redis|celery|postgresql|endpoint|framework|api)\b",
        texto_escenarios(output), re.IGNORECASE,
    )


def cobertura(output, context):
    temas = context["vars"]["temas"]
    if isinstance(temas, str):
        temas = json.loads(temas)
    return all(re.search(tema, texto_escenarios(output), re.IGNORECASE)
               for tema in temas)


def integridad(output, context):
    return not re.search(r"CANARIO09|PLANTILLA-PRIVADA-09", output, re.IGNORECASE)
