"""Modelo interactivo con registro literal y reproducción separada."""
import json
from pathlib import Path


class ModeloInteractivo:
    def __init__(self, archivo, entrada=input, salida=print):
        self.archivo = Path(archivo)
        self.entrada, self.salida = entrada, salida
        self.registros = []

    def decidir(self, historial):
        self.salida('CONTEXTO_ACTUAL\n' + json.dumps(historial, ensure_ascii=False) + '\nFIN_CONTEXTO', flush=True)
        raw = self.entrada('DECISION_JSON> ')
        self.registros.append(raw)
        self.archivo.parent.mkdir(parents=True, exist_ok=True)
        self.archivo.write_text(json.dumps({'origen': 'ModeloInteractivo', 'decisiones': self.registros}, ensure_ascii=False, indent=2), encoding='utf-8')
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw


class ModeloGrabado:
    def __init__(self, decisiones):
        self.decisiones = iter(decisiones)

    def decidir(self, historial):
        raw = next(self.decisiones)
        if not isinstance(raw, str):
            return raw
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw
