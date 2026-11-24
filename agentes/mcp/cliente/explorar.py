"""python -m agentes.mcp.cliente.explorar"""
import json
from .rpc import Cliente

if __name__ == '__main__':
    with Cliente() as cliente:
        for metodo in ('server/discover', 'tools/list', 'resources/list', 'resources/templates/list', 'prompts/list'):
            print(json.dumps(cliente.pedir(metodo), ensure_ascii=False, indent=2))
