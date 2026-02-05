"""Adaptador: Generador de archivos markdown."""

from pathlib import Path

from src.domain.repository.output_generator import OutputGenerator
from src.infrastructure.config.settings import settings
from src.infrastructure.exceptions import OutputGenerationError


class MarkdownOutputGenerator(OutputGenerator):
    """
    Adaptador para escribir archivos markdown.

    Implementa el puerto OutputGenerator escribiendo archivos .md
    """

    def __init__(self, output_dir: Path | None = None):
        """
        Inicializa el generador de output.

        Args:
            output_dir: Directorio de salida (usa settings si no se proporciona)
        """
        self.output_dir = output_dir or settings.output_dir
        self._ensure_output_dir()

    def _ensure_output_dir(self) -> None:
        """Crea el directorio de salida si no existe."""
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise OutputGenerationError(
                f"Cannot create output directory: {str(e)}"
            ) from e

    def save_pom(self, content: str, filename: str = "POM.md") -> Path:
        """Guarda el archivo POM.md."""
        return self._save_file(content, filename)

    def save_pom_components(
        self, content: str, filename: str = "POM-components.md"
    ) -> Path:
        """Guarda el archivo POM-components.md."""
        return self._save_file(content, filename)

    def save_cucumber(self, content: str, filename: str = "cucumber.md") -> Path:
        """Guarda el archivo cucumber.md."""
        return self._save_file(content, filename)

    def save_playwright(self, content: str, filename: str = "playwright.md") -> Path:
        """Guarda el archivo playwright.md."""
        return self._save_file(content, filename)

    def get_output_dir(self) -> Path:
        """Retorna el directorio de salida configurado."""
        return self.output_dir

    def _save_file(self, content: str, filename: str) -> Path:
        """
        Guarda contenido a un archivo.

        Args:
            content: Contenido markdown a guardar
            filename: Nombre del archivo

        Returns:
            Path al archivo guardado

        Raises:
            OutputGenerationError: Si no se puede escribir el archivo
        """
        file_path = self.output_dir / filename

        try:
            file_path.write_text(content, encoding="utf-8")
            return file_path
        except Exception as e:
            raise OutputGenerationError(
                f"Cannot write file {filename}: {str(e)}"
            ) from e

    def clear_output_dir(self) -> None:
        """Limpia todos los archivos .md del directorio de salida."""
        try:
            for md_file in self.output_dir.glob("*.md"):
                md_file.unlink()
        except Exception as e:
            raise OutputGenerationError(
                f"Cannot clear output directory: {str(e)}"
            ) from e
