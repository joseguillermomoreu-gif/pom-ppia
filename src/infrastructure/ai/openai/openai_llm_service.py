"""Adaptador: OpenAI LLM Service."""

import os
import sys
import time
import traceback
from typing import Optional

from openai import OpenAI, OpenAIError
from openai import RateLimitError as OpenAIRateLimitError
from openai import Timeout as OpenAITimeout

from src.domain.repository.llm_service import LLMService
from src.infrastructure.config.settings import settings
from src.infrastructure.exceptions import LLMServiceError, RateLimitError, TimeoutError


class OpenAILLMService(LLMService):
    """
    Adaptador para OpenAI API.

    Implementa el puerto LLMService usando la API de OpenAI.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """
        Inicializa el servicio de OpenAI.

        Args:
            api_key: API key de OpenAI (usa settings si no se proporciona)
            model: Modelo a usar (usa settings si no se proporciona)
            max_retries: Número máximo de reintentos
            retry_delay: Delay inicial entre reintentos (exponential backoff)
        """
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.default_model
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # DEBUG: Verificar variables de entorno relacionadas con proxies
        proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy',
                      'ALL_PROXY', 'NO_PROXY', 'REQUESTS_CA_BUNDLE']
        proxy_env = {var: os.environ.get(var) for var in proxy_vars if os.environ.get(var)}

        if proxy_env:
            print(f"\n⚠️  DEBUG: Variables de proxy detectadas en el entorno:", file=sys.stderr)
            for var, val in proxy_env.items():
                print(f"   {var} = {val}", file=sys.stderr)
            print("   Estas pueden causar conflictos con OpenAI SDK\n", file=sys.stderr)

            # Limpiar variables de proxy temporalmente para evitar conflictos
            for var in proxy_vars:
                if var in os.environ:
                    del os.environ[var]
            print("   ✓ Variables de proxy removidas temporalmente\n", file=sys.stderr)

        # Inicializar cliente OpenAI con solo los parámetros soportados
        try:
            print(f"🔍 DEBUG: Inicializando OpenAI client con modelo: {self.model}", file=sys.stderr)
            print(f"🔍 DEBUG: API key presente: {bool(self.api_key)}", file=sys.stderr)

            self.client = OpenAI(
                api_key=self.api_key,
                timeout=60.0,
                max_retries=0,
            )

            print("✓ DEBUG: Cliente OpenAI inicializado correctamente\n", file=sys.stderr)

        except TypeError as e:
            print(f"\n❌ DEBUG: Error de tipo al inicializar OpenAI:", file=sys.stderr)
            print(f"   Mensaje: {str(e)}", file=sys.stderr)
            print(f"   Tipo: {type(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)

            # Intentar solo con api_key
            print("\n🔄 DEBUG: Intentando inicialización simple (solo api_key)...", file=sys.stderr)
            self.client = OpenAI(api_key=self.api_key)
            print("✓ DEBUG: Inicialización simple exitosa\n", file=sys.stderr)

        except Exception as e:
            print(f"\n❌ DEBUG: Error inesperado al inicializar OpenAI:", file=sys.stderr)
            print(f"   Mensaje: {str(e)}", file=sys.stderr)
            print(f"   Tipo: {type(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            raise LLMServiceError(f"Error al inicializar OpenAI client: {str(e)}") from e

        # Precios por 1K tokens (aproximados, verificar en OpenAI)
        self.pricing = {
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
            "gpt-4o": {"input": 0.0025, "output": 0.010},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-4": {"input": 0.03, "output": 0.06},
        }

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> str:
        """
        Genera una respuesta usando OpenAI.

        Incluye retry con exponential backoff para manejar rate limits.
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        delay = self.retry_delay

        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

                content = response.choices[0].message.content

                if content is None:
                    raise LLMServiceError("Empty response from OpenAI")

                return content

            except OpenAIRateLimitError as e:
                if attempt == self.max_retries - 1:
                    raise RateLimitError(f"Rate limit exceeded: {str(e)}") from e

                print(f"Rate limit hit. Waiting {delay}s before retry...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff

            except OpenAITimeout as e:
                if attempt == self.max_retries - 1:
                    raise TimeoutError(f"Request timeout: {str(e)}") from e

                print(f"Timeout. Retrying in {delay}s...")
                time.sleep(delay)

            except OpenAIError as e:
                raise LLMServiceError(f"OpenAI API error: {str(e)}") from e

            except Exception as e:
                raise LLMServiceError(f"Unexpected error: {str(e)}") from e

        raise LLMServiceError("Max retries exceeded")

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estima el costo de una petición."""
        pricing = self.pricing.get(
            self.model, self.pricing["gpt-4o-mini"]  # Default
        )

        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]

        return input_cost + output_cost

    def count_tokens(self, text: str) -> int:
        """
        Cuenta tokens aproximadamente.

        Nota: Esta es una estimación simplificada.
        Para precisión, usar tiktoken library.
        """
        # Aproximación simple: ~4 caracteres por token en inglés
        # ~6 caracteres por token en español
        return len(text) // 5
