"""Renderiza exactamente la misma entrada para captura, evaluación y ejecución."""

import json
from pathlib import Path
import re

RAIZ = Path(__file__).resolve().parent


def renderizar(tarea, version, datos):
    if tarea not in {"criterios", "commits"} or not re.fullmatch(r"v\d+(?:\.\d+)?", version):
        raise ValueError("Tarea o versión inválida")
    ruta = RAIZ / tarea / f"{version}.txt"
    entrada = json.dumps(datos, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e")
    return ruta.read_text(encoding="utf-8").replace("{{entrada}}", entrada)
