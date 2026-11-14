"""Compara aprobación, mediana de latencia y costo de API por proveedor."""

import argparse
from collections import defaultdict
import json
from pathlib import Path
from statistics import median


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reporte", type=Path)
    args = parser.parse_args()
    filas = json.loads(args.reporte.read_text(encoding="utf-8"))["results"]["results"]
    grupos = defaultdict(list)
    for fila in filas:
        if "output" not in (fila.get("response") or {}):
            parser.error("Una llamada no devolvió respuesta. Revisa el reporte.")
        proveedor = fila["provider"]
        grupos[proveedor.get("label") or proveedor["id"]].append(fila)
    if len(grupos) != 2 or len({len(filas) for filas in grupos.values()}) != 1:
        parser.error("Se requieren dos proveedores con el mismo número de casos")
    print("| Proveedor | Aprobados | Tasa | Mediana (ms) | USD de API por caso |")
    print("| --- | ---: | ---: | ---: | ---: |")
    for proveedor, filas in grupos.items():
        exitos = sum(bool(fila["success"]) for fila in filas)
        evidencias = [json.loads(
            (Path(__file__).parent / "grabaciones" / proveedor / f'{fila["vars"]["id"]}.json')
            .read_text(encoding="utf-8")
        ) for fila in filas]
        latencias = [evidencia["latencia_ms"] for evidencia in evidencias]
        costo = sum(evidencia["costo_usd"] for evidencia in evidencias)
        print(f"| {proveedor} | {exitos}/{len(filas)} | {exitos / len(filas):.1%} | "
              f"{median(latencias):.0f} | {costo / len(filas):.6f} |")


if __name__ == "__main__":
    main()
