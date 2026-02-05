"""Adaptador: Repositorio de tests desde filesystem."""

import re
from pathlib import Path
from typing import List

from src.domain.model.test_file import TestFile
from src.domain.repository.test_repository import TestRepository
from src.domain.service.test_analyzer import TestAnalyzer
from src.infrastructure.exceptions import MCPTestDetectedError, TestFileError


class FileTestRepository(TestRepository):
    """
    Adaptador para leer tests desde el filesystem.

    Implementa el puerto TestRepository leyendo archivos .spec.ts
    """

    def __init__(self):
        """Inicializa el repositorio."""
        self.test_analyzer = TestAnalyzer()

    def list_test_files(self, directory: Path) -> List[Path]:
        """Lista todos los archivos de test en un directorio."""
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        if not directory.is_dir():
            raise ValueError(f"Path is not a directory: {directory}")

        # Buscar archivos .spec.ts recursivamente
        test_files = list(directory.rglob("*.spec.ts"))

        return sorted(test_files)

    def read_test(self, file_path: Path) -> TestFile:
        """Lee y parsea un archivo de test a entidad TestFile."""
        if not file_path.exists():
            raise FileNotFoundError(f"Test file not found: {file_path}")

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            raise TestFileError(f"Error reading file {file_path}: {str(e)}") from e

        # Extraer metadata del test
        test_name = self._extract_test_name(content, file_path)
        objective = self._extract_objective(content)
        strategy = self._extract_strategy(content)

        # Extraer steps
        steps = self.test_analyzer.extract_steps_from_content(content)

        # Crear entidad TestFile
        test_file = TestFile(
            path=file_path,
            content=content,
            test_name=test_name,
            objective=objective,
            steps=steps,
            strategy=strategy,
        )

        # Verificar si es test MCP
        if test_file.is_mcp_test():
            raise MCPTestDetectedError(
                f"Test uses MCP sequences and should be excluded: {file_path.name}"
            )

        return test_file

    def filter_mcp_tests(self, test_files: List[TestFile]) -> List[TestFile]:
        """Filtra tests que usan MCP sequences."""
        return [test for test in test_files if not test.is_mcp_test()]

    def _extract_test_name(self, content: str, file_path: Path) -> str:
        """Extrae el nombre del test desde el contenido o filename."""
        # Buscar en test('nombre', ...)
        pattern = r"test\(['\"]([^'\"]+)['\"]\s*,"
        match = re.search(pattern, content)

        if match:
            return match.group(1)

        # Fallback: usar filename sin extensión
        return file_path.stem.replace(".spec", "").replace("-", " ").title()

    def _extract_objective(self, content: str) -> str:
        """Extrae el objetivo del test desde comentarios."""
        # Buscar en comentarios /** OBJETIVO DEL TEST: */
        objective_pattern = r"\* 🎯 OBJETIVO DEL TEST:\s*\n\s*\* (.+)"
        match = re.search(objective_pattern, content)

        if match:
            return match.group(1).strip()

        # Buscar en comentario simple
        objective_pattern_alt = r"// OBJETIVO: (.+)"
        match = re.search(objective_pattern_alt, content)

        if match:
            return match.group(1).strip()

        return "No objective specified"

    def _extract_strategy(self, content: str) -> str:
        """Extrae la estrategia PPIA usada."""
        # Buscar "STRATEGY: N" o "STRATEGY N"
        strategy_patterns = [
            r"STRATEGY[::\s]+(\d+)",
            r"Strategy\s+(\d+)",
            r"strategy-(\d+)",
        ]

        for pattern in strategy_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return f"Strategy {match.group(1)}"

        return "Unknown Strategy"
