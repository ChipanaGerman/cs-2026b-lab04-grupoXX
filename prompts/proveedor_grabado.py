"""Reproduce respuestas exactas para el caso y la versión solicitados."""

from pathlib import Path
import re

RAIZ = Path(__file__).resolve().parent


def call_api(prompt, options, context):
    config = options["config"]
    tarea, version, caso = config["tarea"], config["version"], context["vars"]["id"]
    if tarea not in {"criterios", "commits", "seguridad", "reto"}:
        return {"error": "Tarea desconocida"}
    if not all(re.fullmatch(r"[a-zA-Z0-9.-]+", valor) and valor not in {".", ".."}
               for valor in (version, caso)):
        return {"error": "Versión o caso inválido"}
    ruta = RAIZ / tarea / "grabaciones" / version / f"{caso}.txt"
    if not ruta.is_file():
        return {"error": f"Falta grabación: {tarea}/{version}/{caso}"}
    return {"output": ruta.read_bytes().decode("utf-8")}
