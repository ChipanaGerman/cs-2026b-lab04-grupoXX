# ISSUE-02: Acepta cantidades inválidas

**Observado:** Cantidad 0 agrega una línea; negativos y bool también pasan.

**Esperado:** Rechazar no enteros o valores menores que 1 antes de mutar.

**Reproducción:** python -m pytest -q tests/test_issue_02.py

Datos ficticios. Error existente en src/pedidos/dominio.py. Ver agentes/evidencia/E1-rojo.txt.
