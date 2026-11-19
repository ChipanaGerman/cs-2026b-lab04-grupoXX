"""Permisos por rol. No se ejecutan órdenes de shell."""
from dataclasses import dataclass


def aprobar_consola(args, entrada=input, salida=print):
    salida(f"Edición propuesta: {args['ruta']}\nANTES:\n{args['antes']}\nDESPUÉS:\n{args['despues']}")
    while True:
        try:
            respuesta = entrada('¿Aprueba esta edición? [s/n]: ').strip().lower()
        except (EOFError, KeyboardInterrupt):
            return False
        if respuesta in {'s', 'n'}:
            return respuesta == 's'
        salida('Respuesta inválida: escriba s o n.')


@dataclass
class Politica:
    rol: str = 'ejecutor'
    max_pasos: int = 12
    aprobar_edicion: object = aprobar_consola

    def evaluar(self, accion, args, paso):
        if paso > self.max_pasos:
            return False, 'Límite de pasos'
        lectura = {'listar_archivos', 'leer_archivo', 'buscar', 'ejecutar_pruebas', 'ver_cambios', 'mapa_repo', 'leer_notas'}
        permitidas = lectura | ({'editar_archivo', 'anotar'} if self.rol == 'ejecutor' else set())
        if accion not in permitidas:
            return False, f'Rol {self.rol}: herramienta no permitida'
        if accion == 'editar_archivo' and args['ruta'].replace('\\', '/') != 'src/pedidos/dominio.py':
            return False, 'Solo se permite editar el archivo de dominio; tests protegidos'
        return True, ''
