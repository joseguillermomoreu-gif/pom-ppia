"""DTOs: Resultados de generación."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


@dataclass
class GenerationResult:
    """
    DTO que encapsula el resultado de una generación.

    Contiene información sobre archivos generados, costos, tiempos, etc.
    """

    success: bool
    """Si la generación fue exitosa"""

    generated_files: Dict[str, Path] = field(default_factory=dict)
    """Archivos generados: {tipo: path}"""

    errors: List[str] = field(default_factory=list)
    """Lista de errores encontrados"""

    warnings: List[str] = field(default_factory=list)
    """Lista de warnings"""

    metadata: Dict[str, any] = field(default_factory=dict)
    """Metadata adicional (tokens, tiempo, costo, etc.)"""

    def add_file(self, file_type: str, file_path: Path) -> None:
        """Añade un archivo generado."""
        self.generated_files[file_type] = file_path

    def add_error(self, error: str) -> None:
        """Añade un error."""
        self.errors.append(error)
        self.success = False

    def add_warning(self, warning: str) -> None:
        """Añade un warning."""
        self.warnings.append(warning)

    def set_metadata(self, key: str, value: any) -> None:
        """Establece metadata."""
        self.metadata[key] = value

    def get_total_files(self) -> int:
        """Retorna el número total de archivos generados."""
        return len(self.generated_files)

    def has_errors(self) -> bool:
        """Verifica si hay errores."""
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        """Verifica si hay warnings."""
        return len(self.warnings) > 0
