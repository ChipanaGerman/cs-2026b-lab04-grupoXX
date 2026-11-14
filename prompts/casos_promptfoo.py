"""Añade a cada caso la entrada serializada que utiliza el proveedor de evaluación."""

from pathlib import Path
import json

import yaml

RAIZ = Path(__file__).resolve().parent


def _casos(tarea):
    casos = yaml.safe_load((RAIZ / tarea / "casos.yaml").read_text(encoding="utf-8"))
    for caso in casos:
        variables = caso["vars"]
        if "temas" in variables:
            variables["temas"] = json.dumps(variables["temas"], ensure_ascii=False)
        campo = "diff" if tarea == "commits" else "historia"
        variables["entrada"] = json.dumps(
            {"id": variables["id"], campo: variables[campo]}, ensure_ascii=False,
        ).replace("<", "\\u003c").replace(">", "\\u003e")
    return casos


def criterios():
    return _casos("criterios")


def commits():
    return _casos("commits")


def seguridad():
    return _casos("seguridad")


def reto():
    return _casos("reto")
