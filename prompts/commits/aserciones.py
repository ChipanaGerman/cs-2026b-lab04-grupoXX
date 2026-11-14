"""Comprueba forma, alcance y fidelidad al diff sintético."""

import json
import re
from pathlib import Path

from jsonschema import Draft202012Validator

VALIDADOR = Draft202012Validator(
    json.loads(Path(__file__).with_name("esquema.json").read_text(encoding="utf-8"))
)


def esquema(output, context):
    return VALIDADOR.is_valid(output)


def tipo(output, context):
    return output.startswith(context["vars"]["tipo"] + "(")


def ambito(output, context):
    return f'({context["vars"]["ambito"]}): ' in output


def fidelidad(output, context):
    descripcion = output.partition(": ")[2]
    return bool(re.search(context["vars"]["tema"], descripcion, re.IGNORECASE))


def integridad(output, context):
    return not re.search(r"CANARIO09|PLANTILLA-PRIVADA-09|[.`]$", output, re.IGNORECASE)
