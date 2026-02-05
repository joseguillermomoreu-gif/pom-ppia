"""Handler para generar CLAUDE.md con guía de refactorización."""

from pathlib import Path
from typing import List

from src.domain.model.test_file import TestFile
from src.domain.repository.llm_service import LLMService
from src.domain.repository.output_generator import OutputGenerator
from src.infrastructure.ai.openai.prompt_builder import PromptBuilder


class GenerateClaudeHandler:
    """
    Genera CLAUDE.md con guía de refactorización.

    Este archivo ayuda a Claude Code a entender cómo refactorizar
    los tests usando la documentación POM generada.
    """

    def __init__(
        self,
        llm_service: LLMService,
        output_generator: OutputGenerator,
    ):
        """
        Inicializa el handler.

        Args:
            llm_service: Servicio LLM para generación
            output_generator: Generador de archivos de salida
        """
        self.llm_service = llm_service
        self.output_generator = output_generator

    def execute(
        self,
        test_files: List[TestFile],
        pom_generated: bool = False,
    ) -> Path:
        """
        Genera CLAUDE.md con guía de refactorización.

        Args:
            test_files: Archivos de test analizados
            pom_generated: Si se generó POM.md

        Returns:
            Path del archivo CLAUDE.md generado
        """
        # Construir prompt para CLAUDE.md
        prompt = PromptBuilder.build_claude_guide_prompt(
            test_files=test_files,
            pom_generated=pom_generated,
        )

        # Generar contenido con LLM
        claude_content = self.llm_service.generate(
            prompt=prompt,
            system_prompt=PromptBuilder.SYSTEM_PROMPT_CLAUDE_GUIDE,
            temperature=0.7,
            max_tokens=4000,
        )

        # Guardar archivo
        claude_path = self.output_generator.save_claude(claude_content)

        return claude_path
