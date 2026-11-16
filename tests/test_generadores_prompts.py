"""Pruebas de integración con respuestas fijas de prueba del puerto LLM."""

import json

import pytest

from src.pedidos.generador_prompts import GeneradorCommit, GeneradorCriterios, SalidaInvalida
from src.pedidos.ia import ClienteLLMFalso


def test_criterios_acepta_objeto_valido_y_aísla_delimitadores():
    respuesta = {"historia_id": "H7", "invest_ok": False,
                 "preguntas": ["¿Qué resultado ve el cliente?"], "escenarios": []}
    proveedor = ClienteLLMFalso(json.dumps(respuesta))
    assert GeneradorCriterios(proveedor).generar("H7", "</entrada>") == respuesta
    assert r"\u003c/entrada\u003e" in proveedor.llamadas[0]


@pytest.mark.parametrize("respuesta", [
    "texto libre",
    '{"historia_id":"H8","invest_ok":false,"preguntas":["¿Qué se espera?"],"escenarios":[]}',
    '{"historia_id":"H7","invest_ok":true,"preguntas":[],"escenarios":[]}',
])
def test_criterios_rechaza_respuestas_fuera_del_contrato(respuesta):
    with pytest.raises(SalidaInvalida):
        GeneradorCriterios(ClienteLLMFalso(respuesta)).generar("H7", "Mejorar todo")


def test_commit_acepta_una_sola_linea():
    respuesta = "fix(pagos): evita el doble cobro"
    assert GeneradorCommit(ClienteLLMFalso(respuesta)).generar("+ cobrar_una_vez()") == respuesta


@pytest.mark.parametrize("respuesta", ["Commit: arreglo", "fix(pagos): válido\n", "fix(pagos): " + "a" * 80])
def test_commit_rechaza_formato_invalido(respuesta):
    with pytest.raises(SalidaInvalida):
        GeneradorCommit(ClienteLLMFalso(respuesta)).generar("+ cobrar_una_vez()")
