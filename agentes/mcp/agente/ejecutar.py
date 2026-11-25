"""ModeloInteractivo del Lab 10. Las decisiones se pegan después de observar."""
import json
from pathlib import Path
from agentes.agente.modelos import ModeloInteractivo
from agentes.agente.nucleo import Agente
from agentes.mcp.agente.herramientas_mcp import HerramientasMCP, PoliticaMCP
from agentes.mcp.cliente.rpc import Cliente

BASE = Path(__file__).resolve().parents[1]
OBJETIVO = ('Consulta el menú de La Tradición para 2026-11-24 y pedidos CANCELADO. '
            'Si el pedido 00000000-0000-0000-0000-000000000001 está cancelado, '
            'solicita aprobación humana para registrar: Pedido cancelado sin explicación; solicito revisión.')

if __name__ == '__main__':
    with Cliente() as c:
        c.pedir('server/discover')
        h = HerramientasMCP(c)
        modelo = ModeloInteractivo(BASE/'trayectorias/consulta-negocio.json')
        agente = Agente('atencion-mcp', modelo, h, PoliticaMCP(), OBJETIVO,
                        BASE/'trazas/agente-negocio.jsonl')
        try:
            print(agente.ejecutar())
        finally:
            c.guardar(BASE/'trazas/negocio.jsonl')
            (BASE/'trayectorias/aprobacion.json').write_text(json.dumps(h.aprobaciones,
                ensure_ascii=False, indent=2), encoding='utf-8')
