# ISSUE-03: Reasigna un repartidor ocupado

**Observado:** asignar_pedido no consulta disponible y cambia el pedido.

**Esperado:** ValueError si ocupado; conservar estado y disponibilidad.

**Reproducción:** python -m pytest -q tests/test_issue_03.py

Datos ficticios. Error existente en src/pedidos/dominio.py. Ver agentes/evidencia/E1-rojo.txt.
