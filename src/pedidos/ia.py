"""
PicanteríaYa — ia.py
Refactor E5: aislar el componente de IA detrás de patrones.

Función de IA para el caso PicanteríaYa (tabla 7 de la guía):
  "Redactar la descripción del plato del día"

Patrones implementados:
  - Strategy + Adapter: ProveedorLLM con GeminiAdapter y OpenAIAdapter intercambiables
  - Decorator (caché): ConCache evita llamadas repetidas al mismo prompt
  - Chain of Responsibility (guardrails): cadena de validaciones que bloquean
    respuestas inválidas (precios inventados, afirmaciones prohibidas, longitud)

Las pruebas usan ClienteLLMFalso: no se necesita clave de API ni conexión.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# <<Strategy>> ProveedorLLM — interfaz común para cualquier proveedor de IA
# ─────────────────────────────────────────────────────────────────────────────

class ProveedorLLM(ABC):
    """<<Strategy>> Interfaz que toda implementación de LLM debe cumplir."""

    @abstractmethod
    def completar(self, prompt: str) -> str:
        """Envía el prompt y devuelve la respuesta como string."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# <<Adapter>> — traduce cada proveedor real a la interfaz ProveedorLLM
# ─────────────────────────────────────────────────────────────────────────────

class GeminiAdapter(ProveedorLLM):
    """
    <<Adapter>> Envuelve el SDK de Google Gemini.
    En producción: importa google.generativeai y llama a generate_content().
    En pruebas: se sustituye por ClienteLLMFalso (Strategy de doble de prueba).
    """

    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key  # Leer de variable de entorno, nunca hardcodear

    def completar(self, prompt: str) -> str:
        # Integración real: descomentada en producción con variable de entorno
        # import google.generativeai as genai
        # genai.configure(api_key=self._api_key)
        # model = genai.GenerativeModel("gemini-1.5-flash")
        # return model.generate_content(prompt).text
        raise NotImplementedError(
            "Configurar GEMINI_API_KEY en .env para usar el proveedor real"
        )


class OpenAIAdapter(ProveedorLLM):
    """<<Adapter>> Envuelve la API de OpenAI/ChatGPT."""

    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key

    def completar(self, prompt: str) -> str:
        raise NotImplementedError(
            "Configurar OPENAI_API_KEY en .env para usar el proveedor real"
        )


class ClienteLLMFalso(ProveedorLLM):
    """
    <<Strategy (doble de prueba)>> LLM simulado para las pruebas.
    Devuelve la respuesta configurada sin llamar a ninguna API.
    """

    def __init__(self, respuesta: str):
        self._respuesta = respuesta
        self.llamadas: list[str] = []

    def completar(self, prompt: str) -> str:
        self.llamadas.append(prompt)
        return self._respuesta


# ─────────────────────────────────────────────────────────────────────────────
# <<Decorator>> ConCache — evita pagar dos veces por el mismo prompt
# ─────────────────────────────────────────────────────────────────────────────

class ConCache(ProveedorLLM):
    """<<Decorator>> Memoriza respuestas para no repetir llamadas costosas."""

    def __init__(self, interno: ProveedorLLM):
        self._interno = interno
        self._cache: dict[str, str] = {}

    def completar(self, prompt: str) -> str:
        if prompt not in self._cache:
            self._cache[prompt] = self._interno.completar(prompt)
        return self._cache[prompt]

    @property
    def cache(self) -> dict:
        return dict(self._cache)


# ─────────────────────────────────────────────────────────────────────────────
# <<Chain of Responsibility>> Guardrails — validan la salida del LLM
# ─────────────────────────────────────────────────────────────────────────────

class Guardrail(ABC):
    """
    <<Chain of Responsibility>> Clase base. Cada guardrail valida el texto
    y pasa al siguiente; si detecta un problema, lanza ValueError.
    """

    def __init__(self, siguiente: Optional["Guardrail"] = None):
        self._siguiente = siguiente

    def validar(self, texto: str) -> str:
        texto = self._aplicar(texto)
        if self._siguiente:
            return self._siguiente.validar(texto)
        return texto

    @abstractmethod
    def _aplicar(self, texto: str) -> str: ...


class SinPrecios(Guardrail):
    """Guardrail 1: bloquea respuestas que incluyan precios (p.ej. 'S/ 2.50')."""

    def _aplicar(self, texto: str) -> str:
        if "S/" in texto or "soles" in texto.lower():
            raise ValueError(
                "Guardrail: la IA incluyó un precio en la descripción del plato"
            )
        return texto


class SinAfirmacionesProhibidas(Guardrail):
    """Guardrail 2: bloquea afirmaciones falsas de salud o garantías."""

    PROHIBIDAS = ["garantizado", "cura", "orgánico certificado", "sin gluten certificado"]

    def _aplicar(self, texto: str) -> str:
        for palabra in self.PROHIBIDAS:
            if palabra in texto.lower():
                raise ValueError(
                    f"Guardrail: afirmación no permitida detectada: '{palabra}'"
                )
        return texto


class LongitudMaxima(Guardrail):
    """Guardrail 3: trunca la respuesta si supera el máximo de caracteres."""

    def __init__(self, maximo: int = 400, siguiente: Optional[Guardrail] = None):
        super().__init__(siguiente)
        self._maximo = maximo

    def _aplicar(self, texto: str) -> str:
        if len(texto) > self._maximo:
            return texto[: self._maximo] + "…"
        return texto


def cadena_guardrails_default() -> Guardrail:
    """Construye la cadena estándar de guardrails para PicanteríaYa."""
    return SinPrecios(
        siguiente=SinAfirmacionesProhibidas(
            siguiente=LongitudMaxima(maximo=400)
        )
    )


# ─────────────────────────────────────────────────────────────────────────────
# Servicio de IA — usa los patrones anteriores
# ─────────────────────────────────────────────────────────────────────────────

class ServicioDescripcionPlato:
    """
    Caso de uso: generar la descripción del plato del día con IA.
    El proveedor LLM es inyectado (Strategy); los guardrails son una cadena
    configurable (Chain of Responsibility).
    """

    def __init__(self, proveedor: ProveedorLLM, guardrails: Optional[Guardrail] = None):
        # ConCache envuelve el proveedor inyectado
        self._proveedor = ConCache(proveedor)
        self._guardrails = guardrails or cadena_guardrails_default()

    def sugerir_descripcion(self, nombre_plato: str) -> str:
        prompt = (
            f"Escribe una descripción atractiva del plato '{nombre_plato}' "
            "de la gastronomía arequipeña. Máximo 80 palabras. "
            "No incluyas precios ni afirmaciones de salud."
        )
        respuesta_bruta = self._proveedor.completar(prompt)
        return self._guardrails.validar(respuesta_bruta)
