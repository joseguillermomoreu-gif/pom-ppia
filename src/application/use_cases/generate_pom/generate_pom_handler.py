"""Handler: GeneratePOM."""

from pathlib import Path
from typing import Dict, List, Optional, Tuple

from src.domain.model.test_file import TestFile
from src.domain.repository.llm_service import LLMService
from src.domain.repository.output_generator import OutputGenerator
from src.infrastructure.ai.openai.prompt_builder import PromptBuilder


class GeneratePOMHandler:
    """
    Handler para generar POM.md y POM-components.md.

    Caso de uso: Dado un conjunto de tests, genera documentación
    de Page Object Model.
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

    def execute(
        self, test_files: List[TestFile], existing_pom_path: Optional[Path] = None
    ) -> tuple[Path, Path]:
        """
        Ejecuta la generación de POM.

        Args:
            test_files: Tests a analizar
            existing_pom_path: Path a POM.md existente (opcional)

        Returns:
            Tupla con (path_pom_md, path_pom_components_md)
        """
        # Leer POM existente si se proporciona
        existing_pom = None
        if existing_pom_path and existing_pom_path.exists():
            existing_pom = existing_pom_path.read_text()

        # Construir prompt
        prompt = self.prompt_builder.build_pom_generation_prompt(
            test_files=test_files, existing_pom=existing_pom
        )

        # Generar con LLM
        response = self.llm_service.generate(
            prompt=prompt,
            system_prompt=PromptBuilder.SYSTEM_PROMPT_POM,
            temperature=0.7,
            max_tokens=4000,
        )

        # Parsear respuesta (separar POM.md y POM-components.md)
        pom_content, components_content = self._parse_response(response)

        # Guardar archivos
        pom_path = self.output_generator.save_pom(pom_content)
        components_path = self.output_generator.save_pom_components(
            components_content
        )

        return pom_path, components_path

    def execute_with_history(
        self,
        test_files: List[TestFile],
        conversation_history: List[Dict[str, str]],
        existing_pom_path: Optional[Path] = None,
    ) -> Tuple[Path, Path, List[Dict[str, str]]]:
        """
        Ejecuta generación de POM manteniendo historial de conversación.

        Args:
            test_files: Tests a analizar
            conversation_history: Historial de conversación
            existing_pom_path: Path a POM.md existente (opcional)

        Returns:
            Tupla (path_pom_md, path_pom_components_md, historial_actualizado)
        """
        # Leer POM existente si se proporciona
        existing_pom = None
        if existing_pom_path and existing_pom_path.exists():
            existing_pom = existing_pom_path.read_text()

        # Construir prompt
        prompt = self.prompt_builder.build_pom_generation_prompt(
            test_files=test_files, existing_pom=existing_pom
        )

        # Generar con LLM manteniendo historial
        response, updated_history = self.llm_service.generate_with_history(
            prompt=prompt,
            conversation_history=conversation_history,
            system_prompt=PromptBuilder.SYSTEM_PROMPT_POM,
            temperature=0.7,
            max_tokens=4000,
        )

        # Parsear respuesta
        pom_content, components_content = self._parse_response(response)

        # Guardar archivos
        pom_path = self.output_generator.save_pom(pom_content)
        components_path = self.output_generator.save_pom_components(
            components_content
        )

        return pom_path, components_path, updated_history

    def _parse_response(self, response: str) -> tuple[str, str]:
        """
        Parsea la respuesta del LLM para separar los dos documentos.

        Args:
            response: Respuesta del LLM

        Returns:
            Tupla con (contenido_pom_md, contenido_components_md)
        """
        # Buscar separadores
        separator = "---"
        parts = response.split(separator)

        if len(parts) >= 2:
            pom_content = parts[0].strip()
            components_content = parts[1].strip()
        else:
            # Si no hay separador claro, intentar por headers
            if "# POM-components.md" in response:
                parts = response.split("# POM-components.md")
                pom_content = parts[0].strip()
                components_content = "# POM-components.md\n" + parts[1].strip()
            else:
                # Fallback: todo en POM.md
                pom_content = response
                components_content = "# POM-components.md\n\n(Ver POM.md)"

        # Limpiar headers si están duplicados
        pom_content = pom_content.replace("# POM.md", "").strip()
        pom_content = "# POM.md\n\n" + pom_content

        return pom_content, components_content
