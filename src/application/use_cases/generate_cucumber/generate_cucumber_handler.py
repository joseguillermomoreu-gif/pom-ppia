"""Handler: GenerateCucumber."""

from pathlib import Path
from typing import Dict, List, Tuple

from src.domain.model.test_file import TestFile
from src.domain.repository.llm_service import LLMService
from src.domain.repository.output_generator import OutputGenerator
from src.infrastructure.ai.openai.prompt_builder import PromptBuilder


class GenerateCucumberHandler:
    """
    Handler para generar cucumber.md.

    Caso de uso: Convierte tests Playwright a Cucumber + Gherkin.
    """

    def __init__(
        self, llm_service: LLMService, output_generator: OutputGenerator
    ):
        """
        Inicializa el handler.

        Args:
            llm_service: Servicio LLM para generación
            output_generator: Generador de archivos de salida
        """
        self.llm_service = llm_service
        self.output_generator = output_generator
        self.prompt_builder = PromptBuilder()

    def execute(self, test_files: List[TestFile]) -> Path:
        """
        Ejecuta la generación de Cucumber.

        Args:
            test_files: Tests a convertir

        Returns:
            Path al archivo cucumber.md generado
        """
        # Construir prompt
        prompt = self.prompt_builder.build_cucumber_generation_prompt(
            test_files=test_files
        )

        # Generar con LLM
        response = self.llm_service.generate(
            prompt=prompt,
            system_prompt=PromptBuilder.SYSTEM_PROMPT_CUCUMBER,
            temperature=0.7,
            max_tokens=4000,
        )

        # Asegurar que tiene header
        if not response.strip().startswith("# "):
            response = "# Cucumber Tests\n\n" + response

        # Guardar archivo
        cucumber_path = self.output_generator.save_cucumber(response)

        return cucumber_path

    def execute_with_history(
        self,
        test_files: List[TestFile],
        conversation_history: List[Dict[str, str]],
    ) -> Tuple[Path, List[Dict[str, str]]]:
        """
        Ejecuta generación de Cucumber manteniendo historial.

        El LLM conoce el POM y Playwright.md generados previamente.

        Args:
            test_files: Tests a convertir
            conversation_history: Historial (incluye POM + Playwright)

        Returns:
            Tupla (path_cucumber_md, historial_actualizado)
        """
        # Prompt que referencia el contexto anterior
        base_prompt = self.prompt_builder.build_cucumber_generation_prompt(
            test_files=test_files
        )

        # Añadir referencia explícita al contexto
        prompt = f"""Usando el POM y los tests refactorizados (playwright.md) que ya \
generaste, ahora crea la versión con Cucumber.

{base_prompt}

IMPORTANTE:
- Usa las mismas clases de POM que definiste
- Referencía los ejemplos de playwright.md que acabas de crear
- Los step definitions deben usar esos Page Objects"""

        # Generar con LLM manteniendo historial
        response, updated_history = self.llm_service.generate_with_history(
            prompt=prompt,
            conversation_history=conversation_history,
            temperature=0.7,
            max_tokens=4000,
        )

        # Asegurar header
        if not response.strip().startswith("# "):
            response = "# Cucumber Tests\n\n" + response

        # Guardar archivo
        cucumber_path = self.output_generator.save_cucumber(response)

        return cucumber_path, updated_history
