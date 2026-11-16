"""Captura respuestas de modelos gratuitos identificados, sin credenciales."""

import argparse
from concurrent.futures import ThreadPoolExecutor
from itertools import islice
import json
from time import perf_counter, sleep
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import yaml

from renderizar import RAIZ, renderizar

URL = "https://ai-gateway.kilo.ai/api/v1/chat/completions"
MODELO = "baidu/ernie-5.5-flash-preview:free"
COMPARACION = "liquid/lfm-3-1.7b:free"


def capturar(modelo, prompt):
    if modelo not in {MODELO, COMPARACION}:
        raise ValueError("Se requiere uno de los dos modelos gratuitos seleccionados")
    datos = json.dumps({
        "model": modelo,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "max_tokens": 2400,
    }).encode()
    solicitud = Request(URL, data=datos, headers={"Content-Type": "application/json"})
    for intento in range(3):
        inicio = perf_counter()
        try:
            with urlopen(solicitud, timeout=45) as respuesta:
                cuerpo = json.load(respuesta)
        except (HTTPError, URLError, TimeoutError) as error:
            if intento == 2 or isinstance(error, HTTPError) and error.code not in {429, 500, 502, 503, 504}:
                raise
            sleep(4 * (intento + 1))
            continue
        latencia = round((perf_counter() - inicio) * 1000)
        opcion = cuerpo["choices"][0]
        texto = opcion["message"]["content"]
        if texto is None and opcion.get("finish_reason") == "length":
            texto = ""
        if not isinstance(texto, str):
            raise ValueError("El proveedor no devolvió texto")
        return texto, {
            "modelo_solicitado": modelo,
            "modelo_reportado": cuerpo.get("model"),
            "latencia_ms": latencia,
            "costo_usd": cuerpo["usage"]["cost"],
            "fin": opcion.get("finish_reason"),
        }


def trabajos(grupo):
    for tarea in ("criterios", "commits", "seguridad"):
        if grupo not in {"todo", tarea}:
            continue
        fuente = "criterios" if tarea == "seguridad" else tarea
        versiones = {
            "criterios": ("v1", "v2", "v3", "v3.1"),
            "commits": ("v1", "v2", "v3", "v3.1"),
            "seguridad": ("v3", "v3.1"),
        }[tarea]
        for version in versiones:
            yield tarea, "grabaciones", version, fuente, version, MODELO, None
    if grupo in {"todo", "repeticiones"}:
        for ronda in ("1", "2", "3"):
            yield "criterios", "repeticiones", ronda, "criterios", "v3.1", MODELO, {"H1", "H7", "H8"}
    if grupo in {"todo", "reto"}:
        yield "criterios", "reto", "ernie", "criterios", "v3.1", MODELO, None
        yield "criterios", "reto", "liquid", "criterios", "v3.1", COMPARACION, None


def cola(grupo):
    for tarea, carpeta, salida, fuente, version, modelo, seleccion in trabajos(grupo):
        dataset = yaml.safe_load((RAIZ / tarea / "casos.yaml").read_text(encoding="utf-8"))
        for fila in dataset:
            caso = fila["vars"]
            identificador = caso["id"]
            if seleccion is not None and identificador not in seleccion:
                continue
            campo = "diff" if fuente == "commits" else "historia"
            destino = RAIZ / tarea / carpeta / salida / f"{identificador}.txt"
            if carpeta == "reto":
                destino = RAIZ / "reto" / "grabaciones" / salida / destino.name
            if destino.exists():
                continue
            prompt = renderizar(fuente, version, {"id": identificador, campo: caso[campo]})
            yield modelo, prompt, destino


def guardar(trabajo):
    modelo, prompt, destino = trabajo
    try:
        texto, evidencia = capturar(modelo, prompt)
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.with_suffix(".json").write_text(json.dumps(evidencia, indent=2) + "\n", encoding="utf-8")
        destino.write_bytes(texto.encode("utf-8"))
        print(destino.relative_to(RAIZ), evidencia["modelo_reportado"], flush=True)
        return True
    except (HTTPError, URLError, TimeoutError, ValueError, KeyError, IndexError) as error:
        print(destino.relative_to(RAIZ), type(error).__name__, str(error), flush=True)
        return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("grupo", choices=["todo", "criterios", "commits", "seguridad", "repeticiones", "reto"])
    parser.add_argument("--limite", type=int)
    parser.add_argument("--concurrencia", type=int, default=3)
    args = parser.parse_args()
    pendientes = list(islice(cola(args.grupo), args.limite))
    normales = [trabajo for trabajo in pendientes if "reto" not in trabajo[2].parts]
    comparacion = [trabajo for trabajo in pendientes if "reto" in trabajo[2].parts]
    with ThreadPoolExecutor(max_workers=args.concurrencia) as ejecutor:
        exitos = list(ejecutor.map(guardar, normales))
    exitos.extend(map(guardar, comparacion))
    return 0 if all(exitos) else 1


if __name__ == "__main__":
    raise SystemExit(main())
