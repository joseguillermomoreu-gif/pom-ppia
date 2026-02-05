"""Value Object: Selector CSS/XPath extraído de un test."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Selector:
    """
    Representa un selector CSS/XPath encontrado en un test.

    Value Object inmutable que encapsula un selector con su contexto.
    """

    value: str
    """Valor del selector (ej: 'input[name="uid"]', '#submit-btn')"""

    element_type: str
    """Tipo de elemento (input, button, link, select, textarea, etc.)"""

    action: str
    """Acción realizada (fill, click, check, select, expect, etc.)"""

    context: str
    """Descripción del contexto donde se usa el selector"""

    def __post_init__(self) -> None:
        """Valida los campos del selector."""
        if not self.value.strip():
            raise ValueError("Selector value cannot be empty")

        if not self.element_type.strip():
            raise ValueError("Element type cannot be empty")

        if not self.action.strip():
            raise ValueError("Action cannot be empty")

    def is_data_testid(self) -> bool:
        """Verifica si el selector usa data-testid."""
        return "data-testid" in self.value

    def is_css_selector(self) -> bool:
        """Verifica si es un selector CSS válido."""
        return not self.value.startswith("//")

    def is_xpath(self) -> bool:
        """Verifica si es un selector XPath."""
        return self.value.startswith("//")

    def get_selector_type(self) -> str:
        """Retorna el tipo de selector."""
        if self.is_data_testid():
            return "data-testid"
        elif self.is_xpath():
            return "xpath"
        else:
            return "css"

    def __str__(self) -> str:
        """Representación en string del selector."""
        return f"{self.action}({self.value}) → {self.element_type}"
