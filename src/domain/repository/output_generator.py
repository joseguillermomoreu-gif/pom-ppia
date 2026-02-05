"""Puerto: Generador de archivos de salida (interface)."""

from abc import ABC, abstractmethod
from pathlib import Path


class OutputGenerator(ABC):
    """
    Puerto de salida: Generador de archivos markdown.

    Define el contrato que debe cumplir cualquier adaptador
    que quiera generar archivos de salida.
    """

    @abstractmethod
    def save_pom(self, content: str, filename: str = "POM.md") -> Path:
        """
        Guarda el archivo POM.md.

        Args:
            content: Contenido markdown del POM
            filename: Nombre del archivo (default: POM.md)

        Returns:
            Path al archivo guardado

        Raises:
            IOError: Si no se puede escribir el archivo
        """
        pass

    @abstractmethod
    def save_pom_components(
        self, content: str, filename: str = "POM-components.md"
    ) -> Path:
        """
        Guarda el archivo POM-components.md.

        Args:
            content: Contenido markdown con implementaciones de componentes
            filename: Nombre del archivo (default: POM-components.md)

        Returns:
            Path al archivo guardado

        Raises:
            IOError: Si no se puede escribir el archivo
        """
        pass

    @abstractmethod
    def save_cucumber(self, content: str, filename: str = "cucumber.md") -> Path:
        """
        Guarda el archivo cucumber.md.

        Args:
            content: Contenido markdown con tests Cucumber
            filename: Nombre del archivo (default: cucumber.md)

        Returns:
            Path al archivo guardado

        Raises:
            IOError: Si no se puede escribir el archivo
        """
        pass

    @abstractmethod
    def save_playwright(self, content: str, filename: str = "playwright.md") -> Path:
        """
        Guarda el archivo playwright.md.

        Args:
            content: Contenido markdown con tests Playwright refactorizados
            filename: Nombre del archivo (default: playwright.md)

        Returns:
            Path al archivo guardado

        Raises:
            IOError: Si no se puede escribir el archivo
        """
        pass

    @abstractmethod
    def save_claude(self, content: str, filename: str = "CLAUDE.md") -> Path:
        """
        Guarda el archivo CLAUDE.md.

        Args:
            content: Guía de refactorización para Claude Code
            filename: Nombre del archivo (default: CLAUDE.md)

        Returns:
            Path al archivo guardado

        Raises:
            IOError: Si no se puede escribir el archivo
        """
        pass

    @abstractmethod
    def get_output_dir(self) -> Path:
        """
        Retorna el directorio de salida configurado.

        Returns:
            Path al directorio de salida
        """
        pass
