"""Herramientas locales acotadas; la raíz siempre debe ser una copia aislada."""
import ast
import difflib
import subprocess
import sys
from pathlib import Path


class Herramientas:
    def __init__(self, raiz):
        self.raiz = Path(raiz).resolve()
        self.original = self._ruta('src/pedidos/dominio.py').read_text(encoding='utf-8')

    def _ruta(self, ruta):
        p = (self.raiz / ruta).resolve()
        if not p.is_relative_to(self.raiz):
            raise PermissionError('Ruta fuera del sandbox')
        relativa = p.relative_to(self.raiz)
        if any(x.startswith('.') or x.lower() in {'credentials', 'secrets'} for x in relativa.parts):
            raise PermissionError('Archivos ocultos o sensibles protegidos')
        return p

    def catalogo(self):
        return {
            'listar_archivos': {'descripcion': 'Lista archivos visibles de src, tests e issues; devuelve rutas.', 'parametros': []},
            'leer_archivo': {'descripcion': 'Lee UTF-8 visible dentro del sandbox; devuelve texto (máximo 24000 caracteres).', 'parametros': ['ruta']},
            'buscar': {'descripcion': 'Busca texto literal en archivos Python de src; devuelve ruta, línea y contenido.', 'parametros': ['texto']},
            'editar_archivo': {'descripcion': 'Sustituye un fragmento único en dominio.py tras aprobación; devuelve OK o error.', 'parametros': ['ruta', 'antes', 'despues']},
            'ejecutar_pruebas': {'descripcion': 'Ejecuta archivo test_issue_01/02/03.py o todos los tests; devuelve código y salida real.', 'parametros': ['seleccion']},
            'ver_cambios': {'descripcion': 'Diff unificado respecto al dominio al inicio de la tarea.', 'parametros': []},
            'mapa_repo': {'descripcion': 'Devuelve rutas, líneas y firmas AST de src sin ejecutar código.', 'parametros': []},
            'anotar': {'descripcion': 'Añade texto no vacío (máximo 2000 caracteres) a notas.md de la tarea.', 'parametros': ['texto']},
            'leer_notas': {'descripcion': 'Lee notas.md de esta tarea, máximo 8000 caracteres.', 'parametros': []},
        }

    def listar_archivos(self):
        return '\n'.join(p.relative_to(self.raiz).as_posix() for carpeta in ('src', 'tests', 'issues') for p in sorted((self.raiz/carpeta).rglob('*')) if p.is_file() and '__pycache__' not in p.parts)

    def leer_archivo(self, ruta):
        return self._ruta(ruta).read_text(encoding='utf-8')[:24000]

    def buscar(self, texto):
        return '\n'.join(f'{p.relative_to(self.raiz).as_posix()}:{n}: {line}' for p in sorted((self.raiz/'src').rglob('*.py')) for n, line in enumerate(p.read_text(encoding='utf-8').splitlines(), 1) if texto in line)

    def editar_archivo(self, ruta, antes, despues):
        p = self._ruta(ruta)
        if p.relative_to(self.raiz).as_posix() != 'src/pedidos/dominio.py':
            raise PermissionError('Archivo protegido')
        texto = p.read_text(encoding='utf-8')
        if not antes or texto.count(antes) != 1:
            raise ValueError('El fragmento debe aparecer exactamente una vez')
        p.write_text(texto.replace(antes, despues), encoding='utf-8')
        return 'OK: edición aplicada'

    def ejecutar_pruebas(self, seleccion):
        opciones = {'01': ['tests/test_issue_01.py'], '02': ['tests/test_issue_02.py'], '03': ['tests/test_issue_03.py'], 'todos': ['tests']}
        if seleccion not in opciones:
            raise ValueError('seleccion: 01, 02, 03 o todos')
        r = subprocess.run([sys.executable, '-m', 'pytest', '-q', '--tb=short', *opciones[seleccion]], cwd=self.raiz, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=30)
        return f'EXIT={r.returncode}\n{r.stdout}\n{r.stderr}'

    def ver_cambios(self):
        actual = self._ruta('src/pedidos/dominio.py').read_text(encoding='utf-8')
        return ''.join(difflib.unified_diff(self.original.splitlines(True), actual.splitlines(True), fromfile='a/src/pedidos/dominio.py', tofile='b/src/pedidos/dominio.py'))

    def mapa_repo(self):
        """E4: firmas AST de src; no importa ni ejecuta los módulos inspeccionados."""
        filas = []
        for p in sorted((self.raiz/'src').rglob('*.py')):
            arbol = ast.parse(p.read_text(encoding='utf-8'))
            for nodo in ast.walk(arbol):
                if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    filas.append(f'{p.relative_to(self.raiz).as_posix()}:{nodo.lineno} {nodo.name}({ast.unparse(nodo.args)})')
        return '\n'.join(filas)

    def anotar(self, texto):
        """Memoria de notas por sandbox, acotada a 8000 caracteres."""
        if not texto.strip() or len(texto) > 2000:
            raise ValueError('Nota no vacía de hasta 2000 caracteres')
        p = self._ruta('notas.md')
        previo = p.read_text(encoding='utf-8') if p.exists() else '# Notas de la tarea\n'
        nuevo = previo+'- '+texto+'\n'
        if len(nuevo) > 8000:
            raise ValueError('Presupuesto de notas agotado')
        p.write_text(nuevo, encoding='utf-8')
        return 'OK: nota guardada'

    def leer_notas(self):
        p = self._ruta('notas.md')
        return p.read_text(encoding='utf-8') if p.exists() else '(sin notas)'


