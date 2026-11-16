"""Generadores del Lab 09 detrás del puerto ProveedorLLM."""

import json
from functools import lru_cache
import re

from jsonschema import Draft202012Validator

from prompts.renderizar import RAIZ, renderizar
from .ia import ProveedorLLM


class SalidaInvalida(ValueError):
    """El borrador no cumple el contrato y debe descartarse."""


@lru_cache(maxsize=2)
def validador(tarea):
    ruta = RAIZ / tarea / "esquema.json"
    return Draft202012Validator(json.loads(ruta.read_text(encoding="utf-8")))


class GeneradorCriterios:
    def __init__(self, proveedor: ProveedorLLM, version="v3.1"):
        self.proveedor = proveedor
        self.version = version

    def generar(self, id_historia: str, historia: str) -> dict:
        if not re.fullmatch(r"[A-Z][A-Z0-9-]{0,31}", id_historia):
            raise ValueError("Identificador de historia inválido")
        prompt = renderizar("criterios", self.version, {"id": id_historia, "historia": historia})
        texto = self.proveedor.completar(prompt)
        try:
            salida = json.loads(texto)
        except (ValueError, TypeError) as error:
            raise SalidaInvalida("La respuesta de criterios no es JSON") from error
        if (not validador("criterios").is_valid(salida)
                or salida["historia_id"] != id_historia):
            raise SalidaInvalida("La respuesta de criterios no cumple el contrato")
        return salida


class GeneradorCommit:
    def __init__(self, proveedor: ProveedorLLM, version="v3"):
        self.proveedor = proveedor
        self.version = version

    def generar(self, diff: str) -> str:
        prompt = renderizar("commits", self.version, {"diff": diff})
        texto = self.proveedor.completar(prompt)
        if not validador("commits").is_valid(texto):
            raise SalidaInvalida("El mensaje de commit no cumple el contrato")
        return texto
