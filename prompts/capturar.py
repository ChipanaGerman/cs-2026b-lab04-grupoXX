"""Imprime un prompt o archiva una respuesta UTF-8 sin transformarla."""

import argparse
from pathlib import Path

import yaml

from renderizar import RAIZ, renderizar


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tarea", choices=["criterios", "commits", "seguridad", "reto"])
    parser.add_argument("version")
    parser.add_argument("id")
    parser.add_argument("--respuesta", type=Path)
    args = parser.parse_args()

    fuente = {"seguridad": "criterios", "reto": "criterios"}.get(args.tarea, args.tarea)
    dataset = fuente if args.tarea == "reto" else args.tarea
    casos = yaml.safe_load((RAIZ / dataset / "casos.yaml").read_text(encoding="utf-8"))
    caso = next((caso["vars"] for caso in casos if caso["vars"]["id"] == args.id), None)
    if caso is None:
        parser.error(f"Caso desconocido: {args.id}")
    version_prompt = "v3.1" if args.tarea == "reto" else args.version
    campo = "historia" if fuente == "criterios" else "diff"
    prompt = renderizar(fuente, version_prompt, {"id": caso["id"], campo: caso[campo]})

    if args.respuesta is None:
        print(prompt, end="")
        return

    import re
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9.-]*", args.version):
        parser.error("Identificador de grabación inválido")
    destino = RAIZ / args.tarea / "grabaciones" / args.version / f"{args.id}.txt"
    contenido = args.respuesta.read_bytes()
    contenido.decode("utf-8")
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("xb") as archivo:
        archivo.write(contenido)


if __name__ == "__main__":
    main()
}
