"""Resume resultados exportados por Promptfoo y genera el gráfico del laboratorio."""

import argparse
from collections import defaultdict
import html
import json
from pathlib import Path


def filas(ruta):
    return json.loads(ruta.read_text(encoding="utf-8"))["results"]["results"]


def resumir(rutas):
    grupos = defaultdict(dict)
    for ruta in rutas:
        for fila in filas(ruta):
            proveedor = fila["provider"]
            version = proveedor.get("label") or proveedor["id"]
            caso = fila["vars"]["id"]
            if "output" not in (fila.get("response") or {}):
                estado = "sin respuesta"
            else:
                estado = "aprobado" if fila["success"] else "falló"
            grupos[(ruta.stem, version)][caso] = estado
    return grupos


def graficar(grupos, destino):
    ancho = 780
    altura = 75 + 38 * len(grupos)
    partes = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{altura}" '
        f'viewBox="0 0 {ancho} {altura}" role="img" aria-label="Aprobación y cobertura">',
        '<rect width="100%" height="100%" fill="#fff"/>',
        '<g font-family="Arial, sans-serif" fill="#19283a">',
        '<text x="24" y="32" font-size="21">PicanteríaYa · resultados de Promptfoo</text>',
    ]
    for i, ((tarea, version), casos) in enumerate(grupos.items()):
        y = 62 + 38 * i
        aprobados = list(casos.values()).count("aprobado")
        evaluados = len(casos) - list(casos.values()).count("sin respuesta")
        barra = round(390 * aprobados / evaluados) if evaluados else 0
        etiqueta = html.escape(f"{tarea} {version}")
        partes.extend([
            f'<text x="24" y="{y + 15}" font-size="14">{etiqueta}</text>',
            f'<rect x="196" y="{y}" width="390" height="20" rx="4" fill="#e7eef5"/>',
            f'<rect x="196" y="{y}" width="{barra}" height="20" rx="4" fill="#167269"/>',
            f'<text x="602" y="{y + 15}" font-size="14">{aprobados}/{evaluados} '
            f'· capturas {evaluados}/{len(casos)}</text>',
        ])
    partes.append("</g></svg>")
    destino.write_text("\n".join(partes) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reportes", nargs="+", type=Path)
    parser.add_argument("--grafico", type=Path, required=True)
    args = parser.parse_args()
    grupos = resumir(args.reportes)
    for (tarea, version), casos in grupos.items():
        print(tarea, version, json.dumps(casos, ensure_ascii=False))
    graficar(grupos, args.grafico)


if __name__ == "__main__":
    main()
