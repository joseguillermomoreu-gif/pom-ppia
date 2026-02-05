"""Puerto: Servicio de LLM (interface)."""

from abc import ABC, abstractmethod
from typing import Optional


class LLMService(ABC):
    """
    Puerto de salida: Servicio para interactuar con LLMs.

    Define el contrato que debe cumplir cualquier adaptador
    de LLM (OpenAI, Anthropic, etc.).
    """

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> str:
        """
        Genera una respuesta usando el LLM.

        Args:
            prompt: Prompt del usuario
            system_prompt: Prompt del sistema (opcional)
            temperature: Temperatura para la generación (0.0 - 2.0)
            max_tokens: Máximo de tokens en la respuesta

        Returns:
            Respuesta generada por el LLM

        Raises:
            LLMServiceError: Si hay error en la API
            RateLimitError: Si se excede el límite de tasa
            TimeoutError: Si la petición tarda demasiado
        """
        pass

    @abstractmethod
    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Estima el costo de una petición.

        Args:
            input_tokens: Número de tokens de entrada
            output_tokens: Número de tokens de salida

        Returns:
            Costo estimado en USD
        """
        pass

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """
        Cuenta el número de tokens en un texto.

        Args:
            text: Texto a contar

        Returns:
            Número de tokens
        """
        pass
