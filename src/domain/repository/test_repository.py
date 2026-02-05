"""Puerto: Repositorio de tests (interface)."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from src.domain.model.test_file import TestFile


class TestRepository(ABC):
    """
    Puerto de salida: Repositorio para leer tests desde el filesystem.

    Define el contrato que debe cumplir cualquier adaptador
    que quiera proveer tests al dominio.
    """

    @abstractmethod
    def list_test_files(self, directory: Path) -> List[Path]:
        """
        Lista todos los archivos de test en un directorio.

        Args:
            directory: Path al directorio a escanear

        Returns:
            Lista de Paths a archivos .spec.ts

        Raises:
            FileNotFoundError: Si el directorio no existe
        """
        pass

    @abstractmethod
    def read_test(self, file_path: Path) -> TestFile:
        """
        Lee y parsea un archivo de test a entidad TestFile.

        Args:
            file_path: Path al archivo .spec.ts

        Returns:
            Entidad TestFile con contenido parseado

        Raises:
            FileNotFoundError: Si el archivo no existe
            ValueError: Si el contenido no es válido
        """
        pass

    @abstractmethod
    def filter_mcp_tests(self, test_files: List[TestFile]) -> List[TestFile]:
        """
        Filtra tests que usan MCP sequences.

        Args:
            test_files: Lista de TestFile a filtrar

        Returns:
            Lista de TestFile sin tests MCP
        """
        pass
