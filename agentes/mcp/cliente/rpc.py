"""Cliente JSON-RPC síncrono y espía de bytes reales por stdio, sin LLM ni red."""
import json
import os
from pathlib import Path
import queue
import subprocess
import sys
import threading
import time

RAIZ = Path(__file__).resolve().parents[3]
SERVIDOR = RAIZ/'agentes/mcp/servidor_mcp/picanteria_mcp.py'
META = {'io.modelcontextprotocol/protocolVersion': '2026-07-28',
        'io.modelcontextprotocol/clientCapabilities': {'elicitation': {'form': {}}}}


class Cliente:
    def __init__(self, servidor=SERVIDOR, entorno=None):
        self.eventos = []
        self.cola = queue.Queue()
        self.errores = []
        self.proceso = subprocess.Popen([sys.executable, '-X', 'utf8', '-B', str(servidor)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=RAIZ, env={**os.environ, **(entorno or {})})
        threading.Thread(target=self._leer, args=(self.proceso.stdout, self.cola.put), daemon=True).start()
        threading.Thread(target=self._leer, args=(self.proceso.stderr, self.errores.append), daemon=True).start()
        self.numero = 0

    @staticmethod
    def _leer(flujo, guardar):
        for linea in iter(flujo.readline, b''):
            guardar(linea)

    def pedir(self, metodo, params=None):
        self.numero += 1
        solicitud = {'jsonrpc': '2.0', 'id': self.numero, 'method': metodo,
                     'params': {**(params or {}), '_meta': META}}
        raw = (json.dumps(solicitud, ensure_ascii=False, separators=(',', ':'))+'\n').encode('utf-8')
        inicio = time.perf_counter()
        self.proceso.stdin.write(raw)
        self.proceso.stdin.flush()
        self.eventos.append({'direccion': 'cliente->servidor', 'mensaje': solicitud, 'bytes': len(raw)})
        while True:
            try:
                salida = self.cola.get(timeout=20)
            except queue.Empty as exc:
                raise TimeoutError(b''.join(self.errores).decode('utf-8', 'replace')) from exc
            respuesta = json.loads(salida)
            self.eventos.append({'direccion': 'servidor->cliente', 'mensaje': respuesta,
                                 'bytes': len(salida), 'latencia_ms': round((time.perf_counter()-inicio)*1000, 3)})
            if respuesta.get('id') == self.numero:
                return respuesta

    def llamar(self, nombre, argumentos, **continuacion):
        return self.pedir('tools/call', {'name': nombre, 'arguments': argumentos, **continuacion})

    def guardar(self, ruta):
        ruta = Path(ruta)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(''.join(json.dumps(e, ensure_ascii=False)+'\n' for e in self.eventos), encoding='utf-8')

    def cerrar(self):
        self.proceso.stdin.close()
        try:
            self.proceso.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.proceso.kill()
            self.proceso.wait()
        self.proceso.stdout.close()
        self.proceso.stderr.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.cerrar()
