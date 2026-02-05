"""Value Object: Estructura propuesta de Page Object Model."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class PageObject:
    """Representa un Page Object identificado."""

    name: str
    """Nombre del Page Object (ej: 'LoginPage', 'NewCustomerPage')"""

    methods: List[str]
    """Lista de métodos públicos del Page Object"""

    selectors: List[str]
    """Lista de selectores usados en este Page Object"""

    path: str
    """Path recomendado (ej: 'tests/pages/login.page.ts')"""

    def __post_init__(self) -> None:
        """Valida los campos del Page Object."""
        if not self.name.strip():
            raise ValueError("PageObject name cannot be empty")

        if not self.path.strip():
            raise ValueError("PageObject path cannot be empty")


@dataclass(frozen=True)
class Component:
    """Representa un componente reutilizable."""

    name: str
    """Nombre del componente (ej: 'FormComponent', 'NavbarComponent')"""

    methods: List[str]
    """Lista de métodos públicos del componente"""

    path: str
    """Path recomendado (ej: 'tests/components/form.component.ts')"""

    def __post_init__(self) -> None:
        """Valida los campos del componente."""
        if not self.name.strip():
            raise ValueError("Component name cannot be empty")

        if not self.path.strip():
            raise ValueError("Component path cannot be empty")


@dataclass(frozen=True)
class POMStructure:
    """
    Estructura completa de Page Object Model propuesta.

    Value Object inmutable que representa la arquitectura POM
    recomendada para los tests.
    """

    pages: Dict[str, PageObject] = field(default_factory=dict)
    """Diccionario de Page Objects indexados por nombre"""

    components: Dict[str, Component] = field(default_factory=dict)
    """Diccionario de Components indexados por nombre"""

    base_path: str = "tests"
    """Path base del directorio de tests"""

    def get_total_pages(self) -> int:
        """Retorna el número total de Page Objects."""
        return len(self.pages)

    def get_total_components(self) -> int:
        """Retorna el número total de Components."""
        return len(self.components)

    def has_pages(self) -> bool:
        """Verifica si tiene Page Objects."""
        return len(self.pages) > 0

    def has_components(self) -> bool:
        """Verifica si tiene Components."""
        return len(self.components) > 0

    def get_page(self, name: str) -> PageObject | None:
        """Obtiene un Page Object por nombre."""
        return self.pages.get(name)

    def get_component(self, name: str) -> Component | None:
        """Obtiene un Component por nombre."""
        return self.components.get(name)

    def __str__(self) -> str:
        """Representación en string de la estructura POM."""
        return (
            f"POMStructure("
            f"pages={self.get_total_pages()}, "
            f"components={self.get_total_components()}, "
            f"base_path='{self.base_path}'"
            f")"
        )
