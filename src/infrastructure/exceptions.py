"""Excepciones personalizadas del dominio."""


class POMPPIAException(Exception):
    """Excepción base para todas las excepciones del proyecto."""

    pass


class LLMServiceError(POMPPIAException):
    """Error en el servicio LLM."""

    pass


class RateLimitError(LLMServiceError):
    """Error de límite de tasa de la API."""

    pass


class TimeoutError(LLMServiceError):
    """Timeout en la petición al LLM."""

    pass


class TestFileError(POMPPIAException):
    """Error relacionado con archivos de test."""

    pass


class MCPTestDetectedError(TestFileError):
    """Test con MCP sequences detectado."""

    pass


class OutputGenerationError(POMPPIAException):
    """Error generando archivos de salida."""

    pass
