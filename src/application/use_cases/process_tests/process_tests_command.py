"""Comando: ProcessTests."""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class ProcessTestsCommand:
    """
    Comando para procesar tests y generar documentación.

    DTO inmutable que encapsula los parámetros del caso de uso.
    """

    input_dir: Path
    """Directorio con archivos de test"""

    test_files: List[Path]
    """Lista de archivos específicos a procesar"""

    pom_md_path: Optional[Path] = None
    """Path a POM.md existente (opcional)"""

    output_dir: Optional[Path] = None
    """Directorio de salida (opcional, usa default)"""

    def __post_init__(self) -> None:
        """Valida el comando."""
        if not self.input_dir.exists():
            raise ValueError(f"Input directory does not exist: {self.input_dir}")

        if self.pom_md_path and not self.pom_md_path.exists():
            raise ValueError(f"POM.md file does not exist: {self.pom_md_path}")

        if not self.test_files:
            raise ValueError("Test files list cannot be empty")
