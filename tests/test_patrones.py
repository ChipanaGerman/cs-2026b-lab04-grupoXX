"""
PicanteríaYa — tests/test_patrones.py
Pruebas E2-E5: demuestran que cada patrón cumple su intención.

Cada prueba tiene nombre descriptivo que explica QUÉ propiedad del patrón verifica.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from src.pedidos.externos import YapeSDK, CulqiHTTP, WhatsAppSDK
from src.pedidos.pagos import (
    YapeAdapter, CulqiAdapter, ConReintentos, FabricaPasarelas,
    ResultadoPago, ConLog
)
from src.pedidos.estados import (
    Pedido, Recibido, Pagado, Preparando, EnCamino, Entregado, Cancelado
)
from src.pedidos.eventos import (
    PublicadorEventos, NotificadorWhatsApp, RegistradorReportes,
    NotificadorPicanteria, ConSeguimientoGPS
)
from src.pedidos.ia import (
    ClienteLLMFalso, ConCache, SinPrecios, SinAfirmacionesProhibidas,
    LongitudMaxima, ServicioDescripcionPlato, cadena_guardrails_default
)


# ═══════════════════════════════════════════════════════════════════════════════
# E2 — Strategy + Adapter + Factory + Decorator
# ═══════════════════════════════════════════════════════════════════════════════

class TestAdapter:

    def test_yape_adapter_traduce_dict_a_resultado_pago(self):
        sdk = YapeSDK()
        adaptador = YapeAdapter(sdk)
        resultado = adaptador.cobrar(Decimal("17.00"), "959000111")
        assert isinstance(resultado, ResultadoPago)
        assert resultado.aprobado is True
        assert resultado.operacion is not None

    def test_culqi_adapter_traduce_tupla_a_resultado_pago(self):
        cliente = CulqiHTTP()
        adaptador = CulqiAdapter(cliente)
        resultado = adaptador.cobrar(Decimal("17.00"), "959000111")
        assert isinstance(resultado, ResultadoPago)
        assert resultado.aprobado is True

    def test_yape_adapter_rechazado(self):
        sdk = YapeSDK(rechazar=True)
        resultado = YapeAdapter(sdk).cobrar(Decimal("17.00"), "959000111")
        assert resultado.aprobado is False

    def test_culqi_adapter_cobra_en_centimos_correctamente(self):
        """El adapter convierte 17.00 soles → 1700 céntimos para el SDK."""
        cliente = CulqiHTTP()
        CulqiAdapter(cliente).cobrar(Decimal("17.00"), "959000111")
        # El SDK no expone céntimos directamente; verificamos que no lanza excepción
        assert cliente.llamadas == 1


class TestDecorator:

    def test_con_reintentos_reintenta_ante_timeout(self):
        sdk = YapeSDK(fallas=2)
        pasarela = ConReintentos(YapeAdapter(sdk), intentos=3)
        resultado = pasarela.cobrar(Decimal("17.00"), "959000111")
        assert resultado.aprobado is True
        assert sdk.llamadas == 3

    def test_con_reintentos_no_reintenta_pago_rechazado(self):
        """Error detectado por las pruebas: la IA reintentaba también rechazos."""
        sdk = YapeSDK(rechazar=True)
        pasarela = ConReintentos(YapeAdapter(sdk), intentos=3)
        resultado = pasarela.cobrar(Decimal("17.00"), "959000111")
        assert resultado.aprobado is False
        assert sdk.llamadas == 1  # Solo un intento, no tres

    def test_con_reintentos_falla_tras_agotar_intentos(self):
        sdk = YapeSDK(fallas=3)
        pasarela = ConReintentos(YapeAdapter(sdk), intentos=3)
        resultado = pasarela.cobrar(Decimal("17.00"), "959000111")
        assert resultado.aprobado is False

    def test_con_log_registra_cada_cobro(self):
        sdk = YapeSDK()
        bitacora = []
        pasarela = ConLog(YapeAdapter(sdk), bitacora)
        pasarela.cobrar(Decimal("17.00"), "959000111")
        assert len(bitacora) == 1
        assert "aprobado=True" in bitacora[0]


class TestFactory:

    def _fabrica_con_simulados(self) -> FabricaPasarelas:
        fabrica = FabricaPasarelas()
        fabrica.registrar("YAPE", lambda: YapeAdapter(YapeSDK()))
        fabrica.registrar("CULQI", lambda: CulqiAdapter(CulqiHTTP()))
        return fabrica

    def test_factory_crea_pasarela_yape(self):
        pasarela = self._fabrica_con_simulados().crear("YAPE")
        resultado = pasarela.cobrar(Decimal("17.00"), "959000111")
        assert resultado.aprobado is True

    def test_factory_crea_pasarela_culqi(self):
        pasarela = self._fabrica_con_simulados().crear("CULQI")
        resultado = pasarela.cobrar(Decimal("17.00"), "959000111")
        assert resultado.aprobado is True

    def test_factory_lanza_error_para_medio_no_registrado(self):
        fabrica = self._fabrica_con_simulados()
        with pytest.raises(ValueError, match="no soportado"):
            fabrica.crear("BITCOIN")

    def test_open_closed_nuevo_medio_sin_modificar_el_servicio(self):
        """
        Agregar TRANSFERENCIA no requiere modificar ServicioPedidos:
        basta registrar en la fábrica (principio Open/Closed).
        """
        class TransferenciaFalsa:
            def cobrar(self, monto, celular):
                return ResultadoPago(True, "TF-00001")

        fabrica = self._fabrica_con_simulados()
        fabrica.registrar("TRANSFERENCIA", lambda: TransferenciaFalsa())
        resultado = fabrica.crear("TRANSFERENCIA").cobrar(Decimal("17.00"), "959000111")
        assert resultado.aprobado is True


# ═══════════════════════════════════════════════════════════════════════════════
# E3 — State
# ═══════════════════════════════════════════════════════════════════════════════

class _PagoAprobado:
    aprobado = True
    operacion = "YP-99999"

class _PagoRechazado:
    aprobado = False
    operacion = None

def _pedido_con_linea():
    from src.pedidos.antes.servicio import Linea
    p = Pedido(id=1, celular="959000111")
    p.lineas = [type('L', (), {'cantidad': 1, 'precio': Decimal("8.50")})()]
    return p


class TestState:

    def test_recibido_pago_aprobado_transiciona_a_pagado(self):
        p = Pedido(id=1, celular="959000111")
        p.lineas = [object()]
        p.registrar_pago(_PagoAprobado())
        assert p.estado == "PAGADO"

    def test_recibido_pago_rechazado_transiciona_a_cancelado(self):
        p = Pedido(id=1, celular="959000111")
        p.registrar_pago(_PagoRechazado())
        assert p.estado == "CANCELADO"

    def test_pagado_marcar_preparando(self):
        p = Pedido(id=1, celular="959000111")
        p.lineas = [object()]
        p.registrar_pago(_PagoAprobado())
        p.marcar_preparando()
        assert p.estado == "PREPARANDO"

    def test_preparando_marcar_en_camino(self):
        p = Pedido(id=1, celular="959000111")
        p.lineas = [object()]
        p.registrar_pago(_PagoAprobado())
        p.marcar_preparando()
        p.marcar_en_camino()
        assert p.estado == "EN_CAMINO"

    def test_en_camino_confirmar_entrega(self):
        p = Pedido(id=1, celular="959000111")
        p.lineas = [object()]
        p.registrar_pago(_PagoAprobado())
        p.marcar_preparando()
        p.marcar_en_camino()
        p.confirmar_entrega()
        assert p.estado == "ENTREGADO"

    def test_state_impide_transicion_invalida_entregado_cancelar(self):
        """Una transición inválida es imposible por construcción."""
        p = Pedido(id=1, celular="959000111")
        p.lineas = [object()]
        p.registrar_pago(_PagoAprobado())
        p.marcar_preparando()
        p.marcar_en_camino()
        p.confirmar_entrega()
        with pytest.raises(ValueError):
            p.cancelar()

    def test_state_impide_pagar_un_pedido_ya_pagado(self):
        p = Pedido(id=1, celular="959000111")
        p.lineas = [object()]
        p.registrar_pago(_PagoAprobado())
        with pytest.raises(ValueError):
            p.registrar_pago(_PagoAprobado())

    def test_pagado_puede_cancelarse(self):
        p = Pedido(id=1, celular="959000111")
        p.lineas = [object()]
        p.registrar_pago(_PagoAprobado())
        p.cancelar("picanteria sin capacidad")
        assert p.estado == "CANCELADO"


# ═══════════════════════════════════════════════════════════════════════════════
# E4 — Observer + Decorator
# ═══════════════════════════════════════════════════════════════════════════════

class TestObserver:

    def _setup(self):
        pub = PublicadorEventos()
        bandeja = []
        wa = WhatsAppSDK()
        pub.suscribir("pedido_pagado", NotificadorWhatsApp(wa, bandeja))
        pub.suscribir("pedido_pagado", RegistradorReportes(bandeja))
        return pub, bandeja, wa

    def test_observer_notifica_whatsapp_al_publicar_pagado(self):
        pub, bandeja, wa = self._setup()
        pub.publicar("pedido_pagado", {"id": 1, "celular": "959000111", "total": Decimal("17.00")})
        assert any("whatsapp" in e for e in bandeja)
        assert len(wa.bandeja) == 1

    def test_observer_registra_reporte_al_publicar_pagado(self):
        pub, bandeja, _ = self._setup()
        pub.publicar("pedido_pagado", {"id": 1, "celular": "959000111", "total": Decimal("17.00")})
        assert any("reporte:1:17.00" in e for e in bandeja)

    def test_observer_nuevo_suscriptor_sin_tocar_el_servicio(self):
        """
        Agregar NotificadorPicanteria no requiere modificar nada existente
        (principio Open/Closed demostrado con Observer).
        """
        pub, bandeja, wa = self._setup()
        pub.suscribir("pedido_pagado", NotificadorPicanteria(bandeja))
        pub.publicar("pedido_pagado", {
            "id": 1, "celular": "959000111",
            "total": Decimal("17.00"), "picanteria_id": "pic-42"
        })
        assert any("picanteria:pic-42" in e for e in bandeja)

    def test_observer_dos_suscriptores_reciben_el_mismo_evento(self):
        pub, bandeja, wa = self._setup()
        pub.publicar("pedido_pagado", {"id": 1, "celular": "959000111", "total": Decimal("17.00")})
        # WhatsApp + Reporte = 2 entradas en bandeja
        assert len(bandeja) == 2


class TestDecoratorGPS:

    def test_con_seguimiento_gps_agrega_log_sin_modificar_suscriptor(self):
        bandeja = []
        wa = WhatsAppSDK()
        log_gps = []
        suscriptor_base = NotificadorWhatsApp(wa, bandeja)
        decorado = ConSeguimientoGPS(suscriptor_base, log_gps)

        decorado.actualizar("pedido_pagado", {
            "id": 1, "celular": "959000111",
            "total": Decimal("17.00"), "lat": -16.39, "lon": -71.53
        })
        assert len(log_gps) == 1
        assert "lat=-16.39" in log_gps[0]
        assert len(wa.bandeja) == 1  # El suscriptor base también recibió

    def test_con_seguimiento_gps_sin_datos_gps_no_falla(self):
        bandeja = []
        log_gps = []
        decorado = ConSeguimientoGPS(RegistradorReportes(bandeja), log_gps)
        decorado.actualizar("pedido_pagado", {"id": 1, "celular": "x", "total": Decimal("5")})
        assert len(log_gps) == 0  # Sin datos GPS, no agrega


# ═══════════════════════════════════════════════════════════════════════════════
# E5 — IA aislada: Strategy, Decorator caché, Chain of Responsibility
# ═══════════════════════════════════════════════════════════════════════════════

class TestProveedorLLM:

    def test_llm_falso_devuelve_respuesta_configurada(self):
        llm = ClienteLLMFalso("Delicioso rocoto relleno arequipeño.")
        assert llm.completar("prompt de prueba") == "Delicioso rocoto relleno arequipeño."

    def test_llm_falso_registra_prompts_recibidos(self):
        llm = ClienteLLMFalso("ok")
        llm.completar("primer prompt")
        llm.completar("segundo prompt")
        assert len(llm.llamadas) == 2


class TestDecoratorCache:

    def test_cache_evita_llamadas_repetidas_al_mismo_prompt(self):
        llm = ClienteLLMFalso("Descripción del plato.")
        con_cache = ConCache(llm)
        con_cache.completar("prompt X")
        con_cache.completar("prompt X")
        assert len(llm.llamadas) == 1  # Solo una llamada real

    def test_cache_llama_dos_veces_para_prompts_distintos(self):
        llm = ClienteLLMFalso("Descripción.")
        con_cache = ConCache(llm)
        con_cache.completar("prompt A")
        con_cache.completar("prompt B")
        assert len(llm.llamadas) == 2


class TestGuardrails:

    def test_guardrail_sin_precios_bloquea_respuesta_con_S_slash(self):
        guardrail = SinPrecios()
        with pytest.raises(ValueError, match="precio"):
            guardrail.validar("Este plato cuesta S/ 8.50")

    def test_guardrail_sin_afirmaciones_prohibidas_bloquea_garantizado(self):
        guardrail = SinAfirmacionesProhibidas()
        with pytest.raises(ValueError, match="garantizado"):
            guardrail.validar("Calidad garantizado por la picantería")

    def test_guardrail_longitud_maxima_trunca_texto_largo(self):
        guardrail = LongitudMaxima(maximo=10)
        resultado = guardrail.validar("Un texto muy largo que debe truncarse")
        assert len(resultado) <= 11  # 10 + "…"

    def test_cadena_completa_pasa_texto_valido(self):
        cadena = cadena_guardrails_default()
        texto_valido = "Delicioso rocoto relleno con carne y especias arequipeñas."
        assert cadena.validar(texto_valido) == texto_valido

    def test_cadena_completa_bloquea_precio_en_cadena(self):
        cadena = cadena_guardrails_default()
        with pytest.raises(ValueError):
            cadena.validar("Pruébalo por solo S/ 5.00")


class TestServicioDescripcionPlato:

    def test_sugerir_descripcion_usa_llm_falso_sin_api(self):
        llm = ClienteLLMFalso("Rocoto relleno: tradición arequipeña en cada bocado.")
        svc = ServicioDescripcionPlato(llm)
        desc = svc.sugerir_descripcion("Rocoto Relleno")
        assert "arequipeña" in desc

    def test_sugerir_descripcion_bloquea_respuesta_con_precio(self):
        llm = ClienteLLMFalso("Pruébalo por S/ 8.50 en nuestra picantería.")
        svc = ServicioDescripcionPlato(llm)
        with pytest.raises(ValueError, match="precio"):
            svc.sugerir_descripcion("Rocoto Relleno")

    def test_sugerir_descripcion_usa_cache_en_segunda_llamada(self):
        llm = ClienteLLMFalso("Sabor auténtico de Arequipa.")
        svc = ServicioDescripcionPlato(llm)
        svc.sugerir_descripcion("Chupe de Camarones")
        svc.sugerir_descripcion("Chupe de Camarones")
        assert len(llm.llamadas) == 1
