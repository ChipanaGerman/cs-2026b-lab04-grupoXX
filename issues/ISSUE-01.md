# ISSUE-01: El total omite el delivery

**Observado:** Dos platos de S/20 y delivery S/5.50 devuelven S/40.

**Esperado:** S/45.50, sin acumular delivery en llamadas sucesivas.

**Reproducción:** python -m pytest -q tests/test_issue_01.py

Datos ficticios. Error existente en src/pedidos/dominio.py. Ver agentes/evidencia/E1-rojo.txt.
