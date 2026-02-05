"""Handler principal: ProcessTests."""

import time
from typing import List

from src.application.dto.generation_result import GenerationResult
from src.application.use_cases.generate_cucumber.generate_cucumber_handler import (
    GenerateCucumberHandler,
)
from src.application.use_cases.generate_playwright.generate_playwright_handler import (
    GeneratePlaywrightHandler,
)
from src.application.use_cases.generate_pom.generate_pom_handler import (
    GeneratePOMHandler,
)
from src.application.use_cases.process_tests.process_tests_command import (
    ProcessTestsCommand,
)
from src.domain.model.test_file import TestFile
from src.domain.repository.llm_service import LLMService
from src.domain.repository.output_generator import OutputGenerator
from src.domain.repository.test_repository import TestRepository
from src.domain.service.test_analyzer import TestAnalyzer
from src.infrastructure.exceptions import MCPTestDetectedError


class ProcessTestsHandler:
    """
    Handler principal que orquesta el flujo completo.

    Este es el caso de uso de más alto nivel que coordina
    todos los demás use cases.
    """

    def __init__(
        self,
        test_repository: TestRepository,
        test_analyzer: TestAnalyzer,
        llm_service: LLMService,
        output_generator: OutputGenerator,
    ):
        """
        Inicializa el handler principal.

        Args:
            test_repository: Repositorio de tests
            test_analyzer: Servicio de análisis de tests
            llm_service: Servicio LLM
            output_generator: Generador de salida
        """
        self.test_repository = test_repository
        self.test_analyzer = test_analyzer
        self.llm_service = llm_service
        self.output_generator = output_generator

        # Inicializar handlers específicos
        self.pom_handler = GeneratePOMHandler(llm_service, output_generator)
        self.cucumber_handler = GenerateCucumberHandler(
            llm_service, output_generator
        )
        self.playwright_handler = GeneratePlaywrightHandler(
            llm_service, output_generator
        )

    def execute(self, command: ProcessTestsCommand) -> GenerationResult:
        """
        Ejecuta el flujo completo de procesamiento.

        Flujo:
        1. Leer archivos de test
        2. Filtrar tests MCP
        3. Analizar tests
        4. Generar POM
        5. Generar Cucumber
        6. Generar Playwright
        7. Retornar resultado

        Args:
            command: Comando con parámetros

        Returns:
            GenerationResult con archivos generados y metadata
        """
        result = GenerationResult(success=True)
        start_time = time.time()

        try:
            # Paso 1: Leer archivos de test
            test_files = self._read_test_files(command.test_files, result)

            if not test_files:
                result.add_error("No valid test files to process")
                return result

            result.set_metadata("test_count", len(test_files))

            # Paso 2: Analizar tests
            analysis = self.test_analyzer.analyze_tests(test_files)
            result.set_metadata("analysis", analysis)

            # Paso 3: Generar POM
            pom_path, components_path = self.pom_handler.execute(
                test_files=test_files, existing_pom_path=command.pom_md_path
            )
            result.add_file("pom", pom_path)
            result.add_file("pom_components", components_path)

            # Paso 4: Generar Cucumber
            cucumber_path = self.cucumber_handler.execute(test_files=test_files)
            result.add_file("cucumber", cucumber_path)

            # Paso 5: Generar Playwright
            playwright_path = self.playwright_handler.execute(
                test_files=test_files
            )
            result.add_file("playwright", playwright_path)

            # Metadata final
            end_time = time.time()
            result.set_metadata("duration_seconds", round(end_time - start_time, 2))
            result.set_metadata("output_dir", str(self.output_generator.get_output_dir()))

        except Exception as e:
            result.add_error(f"Unexpected error: {str(e)}")

        return result

    def _read_test_files(
        self, test_paths: List, result: GenerationResult
    ) -> List[TestFile]:
        """
        Lee archivos de test y filtra MCP.

        Args:
            test_paths: Lista de paths a archivos de test
            result: Resultado para añadir warnings

        Returns:
            Lista de TestFile válidos (sin MCP)
        """
        test_files: List[TestFile] = []
        mcp_count = 0

        for test_path in test_paths:
            try:
                test_file = self.test_repository.read_test(test_path)
                test_files.append(test_file)

            except MCPTestDetectedError as e:
                # Test con MCP detectado - añadir warning pero continuar
                result.add_warning(str(e))
                mcp_count += 1

            except Exception as e:
                # Otro error - añadir warning y continuar
                result.add_warning(f"Error reading {test_path.name}: {str(e)}")

        if mcp_count > 0:
            result.set_metadata("mcp_tests_excluded", mcp_count)

        return test_files
