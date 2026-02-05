"""Value Object: Paso de test (Given/When/Then)."""

from dataclasses import dataclass
from typing import List

from src.domain.model.selector import Selector


@dataclass(frozen=True)
class TestStep:
    """
    Representa un paso de test con formato BDD (Given/When/Then/And).

    Value Object inmutable que encapsula un step de test.
    """

    step_type: str
    """Tipo de step: 'given', 'when', 'then', 'and'"""

    description: str
    """Descripción del step (ej: 'Usuario inicia sesión')"""

    actions: List[str]
    """Lista de acciones realizadas (fill, click, expect, etc.)"""

    selectors: List[Selector]
    """Lista de selectores usados en este step"""

    def __post_init__(self) -> None:
        """Valida los campos del test step."""
        valid_types = {"given", "when", "then", "and"}
        if self.step_type.lower() not in valid_types:
            raise ValueError(
                f"Invalid step type: {self.step_type}. "
                f"Must be one of {valid_types}"
            )

        if not self.description.strip():
            raise ValueError("Description cannot be empty")

        # Convertir step_type a lowercase
        object.__setattr__(self, "step_type", self.step_type.lower())

    def has_selectors(self) -> bool:
        """Verifica si el step tiene selectores."""
        return len(self.selectors) > 0

    def get_gherkin_prefix(self) -> str:
        """Retorna el prefijo Gherkin apropiado."""
        prefixes = {
            "given": "Given:",
            "when": "When:",
            "then": "Then:",
            "and": "And:",
        }
        return prefixes.get(self.step_type, "And:")

    def to_gherkin(self) -> str:
        """Convierte el step a formato Gherkin."""
        return f"{self.get_gherkin_prefix()} {self.description}"

    def __str__(self) -> str:
        """Representación en string del test step."""
        return self.to_gherkin()
