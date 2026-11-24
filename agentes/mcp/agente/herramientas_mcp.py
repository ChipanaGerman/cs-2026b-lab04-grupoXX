"""Adaptador síncrono para el contrato de herramientas del Lab 10."""
import json
from agentes.mcp.cliente.rpc import Cliente


class HerramientasMCP:
    def __init__(self, cliente: Cliente, aprobar=input):
        self.cliente, self.aprobar = cliente, aprobar
        self.aprobaciones = []
        tools = cliente.pedir('tools/list')['result']['tools']
        self._catalogo = {t['name']: {'descripcion': t['description'],
            'parametros': list(t['inputSchema']['properties'])} for t in tools}

    def catalogo(self):
        return self._catalogo

    def _llamar(self, nombre, argumentos):
        r = self.cliente.llamar(nombre, argumentos)
        if r.get('result', {}).get('resultType') == 'input_required':
            interino = r['result']
            pregunta = interino['inputRequests']['confirmar']['params']['message']
            aceptado = self.aprobar(pregunta+' [s/n]: ').strip().casefold() == 's'
            self.aprobaciones.append({'pregunta': pregunta, 'aceptado': aceptado,
                                      'origen': 'respuesta humana explícita'})
            r = self.cliente.llamar(nombre, argumentos, requestState=interino['requestState'],
                inputResponses={'confirmar': {'action': 'accept' if aceptado else 'decline',
                                             'content': {'confirmar': aceptado}}})
        return json.dumps(r, ensure_ascii=False)

    def menu_del_dia(self, fecha, picanteria):
        return self._llamar('menu_del_dia', dict(fecha=fecha, picanteria=picanteria))

    def pedidos_por_estado(self, estado):
        return self._llamar('pedidos_por_estado', dict(estado=estado))

    def registrar_reclamo(self, pedido_id, descripcion):
        return self._llamar('registrar_reclamo', dict(pedido_id=pedido_id, descripcion=descripcion))


class PoliticaMCP:
    max_pasos = 12

    def evaluar(self, accion, args, paso):
        if paso > self.max_pasos:
            return False, 'Presupuesto agotado'
        return (accion in {'menu_del_dia', 'pedidos_por_estado', 'registrar_reclamo'},
                'Solo catálogo MCP aprobado; el adaptador tramita aprobación humana MRTR')
