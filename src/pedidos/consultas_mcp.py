"""Servicios de aplicación del catálogo MCP; datos sintéticos reproducibles."""
from datetime import datetime
from decimal import Decimal
from pathlib import Path
import json
import re
from uuid import UUID, uuid4

from .dominio import Cliente, EstadoPedido, Menu, Pedido, Picanteria, Plato


class ConsultasPicanteria:
    def __init__(self, carpeta_reclamos):
        self.carpeta = Path(carpeta_reclamos)
        self.picanteria = Picanteria('La Tradición', 'Local ficticio', 'Yanahuara', '')
        self.menu = Menu(datetime(2026, 11, 24), platos=[
            Plato('Rocoto relleno', 'Con pastel de papa', Decimal('25.00'), 12),
            Plato('Chupe de camarones', 'Porción del día', Decimal('35.50'), 8),
            Plato('Adobo', 'Agotado', Decimal('22.00'), 0),
        ])
        self.picanteria.publicar_menu(self.menu)
        self.pedidos = []
        for i, estado in enumerate((EstadoPedido.CANCELADO, EstadoPedido.PAGADO, EstadoPedido.EN_CAMINO), 1):
            pedido = Pedido(Cliente('Cliente ficticio', '', 'Yanahuara'), self.picanteria,
                            id=UUID(int=i), fecha=datetime(2026, 11, 24))
            pedido.agregar_linea(self.menu.platos[0], i)
            pedido.calcular_total()
            pedido.estado = estado
            self.pedidos.append(pedido)

    def menu_del_dia(self, fecha, picanteria):
        if not isinstance(fecha, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', fecha):
            raise ValueError('Use fecha AAAA-MM-DD, por ejemplo 2026-11-24')
        try:
            dia = datetime.strptime(fecha, '%Y-%m-%d').date()
        except ValueError as exc:
            raise ValueError('Fecha inexistente; use AAAA-MM-DD válido') from exc
        if not isinstance(picanteria, str) or not 1 <= len(picanteria.strip()) <= 80:
            raise ValueError('picanteria: texto de 1 a 80 caracteres')
        if picanteria.casefold().strip() != self.picanteria.nombre.casefold():
            raise ValueError('Picantería ficticia disponible: La Tradición')
        if dia != self.menu.fecha.date():
            raise ValueError('Datos ficticios disponibles para 2026-11-24')
        return {'fecha': fecha, 'picanteria': self.picanteria.nombre, 'platos': [
            {'nombre': p.nombre, 'precio_soles': str(p.precio_unitario), 'stock': p.stock_disponible}
            for p in self.menu.obtener_platos_disponibles()]}

    def pedidos_por_estado(self, estado):
        if not isinstance(estado, str) or estado not in EstadoPedido.__members__:
            raise ValueError('estado válido: '+', '.join(EstadoPedido.__members__))
        return {'estado': estado, 'pedidos': [
            {'pedido_id': str(p.id), 'total_soles': str(p.total_calculado)}
            for p in self.pedidos if p.estado.value == estado][:20]}

    def validar_reclamo(self, pedido_id, descripcion):
        try:
            identificador = UUID(pedido_id)
        except (ValueError, TypeError, AttributeError) as exc:
            raise ValueError('pedido_id debe ser un UUID válido') from exc
        if not any(p.id == identificador for p in self.pedidos):
            raise ValueError('Pedido ficticio no encontrado; consulte pedidos_por_estado')
        if not isinstance(descripcion, str) or not 10 <= len(descripcion.strip()) <= 1000:
            raise ValueError('descripcion debe tener de 10 a 1000 caracteres')
        return str(identificador), descripcion.strip()

    def registrar_reclamo(self, pedido_id, descripcion):
        pedido_id, descripcion = self.validar_reclamo(pedido_id, descripcion)
        self.carpeta.mkdir(parents=True, exist_ok=True)
        if self.carpeta.is_symlink():
            raise ValueError('La carpeta de reclamos no puede ser un enlace')
        identificador = str(uuid4())
        registro = {'reclamo_id': identificador, 'pedido_id': pedido_id, 'descripcion': descripcion}
        with (self.carpeta / (identificador+'.json')).open('x', encoding='utf-8') as archivo:
            json.dump(registro, archivo, ensure_ascii=False, indent=2)
        return {'reclamo_id': identificador, 'pedido_id': pedido_id, 'creado': True}
