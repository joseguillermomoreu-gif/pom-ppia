"""Handler para generar CLAUDE.md con guía de refactorización."""

from pathlib import Path
from typing import Dict, List, Tuple

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

    def execute_with_history(
        self,
        test_files: List[TestFile],
        conversation_history: List[Dict[str, str]],
        pom_generated: bool = True,
    ) -> Tuple[Path, List[Dict[str, str]]]:
        """
        Ejecuta generación de CLAUDE.md manteniendo historial.

        El LLM conoce TODO el contexto: POM, Playwright y Cucumber.

        Args:
            test_files: Tests analizados
            conversation_history: Historial completo
            pom_generated: Si se generó POM

        Returns:
            Tupla (path_claude_md, historial_actualizado)
        """
        # Prompt final que usa TODO el contexto
        prompt = """Ahora, usando TODA la documentación que acabas de generar (POM.md, POM-components.md, playwright.md y cucumber.md), crea un archivo CLAUDE.md.

Este archivo es una GUÍA para Claude Code (asistente IA) que ayudará al usuario a:
1. Implementar el POM que diseñaste
2. Migrar los tests originales usando ese POM
3. Elegir entre Playwright simple o Cucumber

## Estructura de CLAUDE.md:

### 1. Introducción
- Qué es este proyecto de refactorización
- Qué archivos se generaron y para qué sirven

### 2. El POM Diseñado
- Resumen de la estructura POM creada
- Page Objects principales
- Dónde crear cada archivo

### 3. Guía de Implementación
**Paso 1:** Crear estructura de directorios
**Paso 2:** Implementar Page Objects (usando POM-components.md)
**Paso 3:** Elegir enfoque:
   - Opción A: Tests con Playwright (ver playwright.md)
   - Opción B: Tests con Cucumber (ver cucumber.md)

### 4. Comandos Útiles
- Cómo ejecutar tests
- Cómo añadir nuevos Page Objects
- Troubleshooting común

### 5. Para Claude Code
Instrucciones específicas para que Claude Code asista en:
- Creación de Page Objects
- Migración de selectores
- Debugging de tests

FORMATO: Markdown claro, conciso, con ejemplos concretos basados en la documentación que ya generaste."""

        # Generar con LLM manteniendo TODO el historial
        response, updated_history = self.llm_service.generate_with_history(
            prompt=prompt,
            conversation_history=conversation_history,
            temperature=0.7,
            max_tokens=4000,
        )

        # Asegurar header
        if not response.strip().startswith("# "):
            response = "# CLAUDE.md - Guía de Refactorización\n\n" + response

        # Guardar archivo
        claude_path = self.output_generator.save_claude(response)

        return claude_path, updated_history
