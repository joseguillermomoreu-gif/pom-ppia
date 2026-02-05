"""Contenedor de inyección de dependencias."""

from src.domain.repository.llm_service import LLMService
from src.domain.repository.output_generator import OutputGenerator
from src.domain.repository.test_repository import TestRepository
from src.domain.service.test_analyzer import TestAnalyzer
from src.infrastructure.ai.openai.openai_llm_service import OpenAILLMService
from src.infrastructure.config.settings import settings
from src.infrastructure.persistence.filesystem.file_test_repository import (
    FileTestRepository,
)
from src.infrastructure.persistence.filesystem.markdown_output_generator import (
    MarkdownOutputGenerator,
)


class DIContainer:
    """
    Contenedor de inyección de dependencias.

    Centraliza la creación de todas las dependencias del sistema
    siguiendo el principio de Dependency Inversion (SOLID).
    """

    _test_repository: TestRepository | None = None
    _llm_service: LLMService | None = None
    _output_generator: OutputGenerator | None = None
    _test_analyzer: TestAnalyzer | None = None

    @classmethod
    def get_test_repository(cls) -> TestRepository:
        """
        Retorna instancia de TestRepository.

        Singleton pattern para reutilizar la instancia.
        """
        if cls._test_repository is None:
            cls._test_repository = FileTestRepository()

        return cls._test_repository

    @classmethod
    def get_llm_service(cls) -> LLMService:
        """
        Retorna instancia de LLMService.

        Por defecto usa OpenAI, pero podría cambiar a Anthropic
        según configuración.
        """
        if cls._llm_service is None:
            if settings.llm_provider == "openai":
                cls._llm_service = OpenAILLMService(
                    api_key=settings.openai_api_key, model=settings.default_model
                )
            # Futuro: elif settings.llm_provider == "anthropic":
            #     cls._llm_service = AnthropicLLMService(...)
            else:
                # Fallback a OpenAI
                cls._llm_service = OpenAILLMService()

        return cls._llm_service

    @classmethod
    def get_output_generator(cls) -> OutputGenerator:
        """Retorna instancia de OutputGenerator."""
        if cls._output_generator is None:
            cls._output_generator = MarkdownOutputGenerator(
                output_dir=settings.output_dir
            )

        return cls._output_generator

    @classmethod
    def get_test_analyzer(cls) -> TestAnalyzer:
        """Retorna instancia de TestAnalyzer (domain service)."""
        if cls._test_analyzer is None:
            cls._test_analyzer = TestAnalyzer()

        return cls._test_analyzer

    @classmethod
    def get_process_tests_handler(cls):
        """
        Retorna instancia de ProcessTestsHandler.

        Importación lazy para evitar dependencias circulares.
        """
        from src.application.use_cases.process_tests.process_tests_handler import (
            ProcessTestsHandler,
        )

        return ProcessTestsHandler(
            test_repository=cls.get_test_repository(),
            test_analyzer=cls.get_test_analyzer(),
            llm_service=cls.get_llm_service(),
            output_generator=cls.get_output_generator(),
        )

    @classmethod
    def reset(cls) -> None:
        """
        Resetea todas las instancias singleton.

        Útil para testing.
        """
        cls._test_repository = None
        cls._llm_service = None
        cls._output_generator = None
        cls._test_analyzer = None
