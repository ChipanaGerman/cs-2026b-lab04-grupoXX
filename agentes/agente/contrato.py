"""Contrato cerrado: una acción o un resultado final, nunca ambos."""
def validar_decision(d, catalogo):
    if not isinstance(d, dict):
        return False, 'Se requiere objeto JSON'
    if not isinstance(d.get('pensamiento'), str) or not d['pensamiento'].strip():
        return False, 'pensamiento debe ser texto no vacío'
    if ('accion' in d) == ('final' in d):
        return False, 'Debe incluir accion o final exclusivamente'
    if 'final' in d:
        if set(d) != {'pensamiento', 'final'} or not isinstance(d['final'], str) or not d['final'].strip():
            return False, 'final no vacío y sin campos extra'
        return True, ''
    if set(d) != {'pensamiento', 'accion', 'args'}:
        return False, 'Campos requeridos: pensamiento, accion, args'
    if not isinstance(d['accion'], str) or d['accion'] not in catalogo:
        return False, 'Herramienta desconocida'
    if not isinstance(d['args'], dict):
        return False, 'args debe ser objeto'
    parametros = catalogo[d['accion']]['parametros']
    if set(d['args']) != set(parametros):
        return False, 'Parámetros no coinciden con el catálogo'
    if any(not isinstance(d['args'][k], str) for k in parametros):
        return False, 'Todos los parámetros de estas herramientas son texto'
    return True, ''
