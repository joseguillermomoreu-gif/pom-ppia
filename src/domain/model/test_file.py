"""Entidad: Test File TypeScript."""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from src.domain.model.selector import Selector
from src.domain.model.test_step import TestStep


@dataclass
class TestFile:
    """
    Entidad que representa un archivo de test TypeScript.

    Esta es la entidad principal del dominio que encapsula
    toda la información de un test Playwright.
    """

    path: Path
    """Path al archivo de test"""

    content: str
    """Contenido completo del archivo"""

    test_name: str
    """Nombre del test"""

    objective: str
    """Objetivo/descripción del test"""

    steps: List[TestStep] = field(default_factory=list)
    """Lista de steps del test"""

    strategy: str = ""
    """Estrategia PPIA usada (Strategy 1, 2, etc.)"""

    def __post_init__(self) -> None:
        """Valida los campos de la entidad."""
        if not self.path.exists():
            raise ValueError(f"Test file does not exist: {self.path}")

        if not self.test_name.strip():
            raise ValueError("Test name cannot be empty")

        if not self.content.strip():
            raise ValueError("Test content cannot be empty")

    def is_mcp_test(self) -> bool:
        """
        Verifica si el test usa MCP sequences.

        Los tests con MCP no deben ser procesados según requisitos.
        """
        mcp_indicators = [
            "MCPUse.executeSequence",
            "from '@ppia/mcp/MCPUse'",
            "import { MCPUse }",
            "MCPAction[]",
        ]

        return any(indicator in self.content for indicator in mcp_indicators)

    def extract_selectors(self) -> List[Selector]:
        """
        Extrae todos los selectores del contenido del test.

        Retorna:
            Lista de objetos Selector encontrados en el test
        """
        selectors: List[Selector] = []

        # Patrones para diferentes tipos de selectores
        patterns = {
            # page.locator('selector').fill('value')
            "fill": r"page\.locator\(['\"](.+?)['\"]\)\.fill\(",
            # page.locator('selector').click()
            "click": r"page\.locator\(['\"](.+?)['\"]\)\.click\(",
            # page.locator('selector') generic
            "generic": r"page\.locator\(['\"](.+?)['\"]\)",
            # expect(page.locator('selector'))
            "expect": r"expect\(page\.locator\(['\"](.+?)['\"]\)\)",
        }

        for action, pattern in patterns.items():
            matches = re.finditer(pattern, self.content)
            for match in matches:
                selector_value = match.group(1)

                # Determinar tipo de elemento basado en el selector
                element_type = self._infer_element_type(selector_value)

                # Extraer contexto (líneas cercanas)
                context = self._extract_context(selector_value)

                selector = Selector(
                    value=selector_value,
                    element_type=element_type,
                    action=action if action != "generic" else "interact",
                    context=context,
                )

                selectors.append(selector)

        return selectors

    def _infer_element_type(self, selector: str) -> str:
        """Infiere el tipo de elemento del selector."""
        selector_lower = selector.lower()

        if "button" in selector_lower or 'type="submit"' in selector_lower:
            return "button"
        elif "input" in selector_lower:
            if 'type="text"' in selector_lower or 'name=' in selector_lower:
                return "input"
            elif 'type="checkbox"' in selector_lower:
                return "checkbox"
            elif 'type="radio"' in selector_lower:
                return "radio"
            return "input"
        elif "select" in selector_lower:
            return "select"
        elif "textarea" in selector_lower:
            return "textarea"
        elif "a" in selector_lower or "link" in selector_lower:
            return "link"
        else:
            return "element"

    def _extract_context(self, selector: str) -> str:
        """Extrae el contexto del selector desde los comentarios."""
        # Buscar en comentarios de test.step()
        step_pattern = r"test\.step\(['\"](.+?)['\"]\s*,\s*async"
        matches = re.finditer(step_pattern, self.content)

        for match in matches:
            step_desc = match.group(1)
            # Buscar si el selector está cerca de este step
            start_pos = match.start()
            end_pos = min(match.end() + 500, len(self.content))
            chunk = self.content[start_pos:end_pos]

            if selector in chunk:
                return step_desc

        return "General context"

    def get_page_objects(self) -> Dict[str, List[str]]:
        """
        Identifica posibles Page Objects agrupando selectores por página/sección.

        Retorna:
            Diccionario con nombre de página como key y lista de selectores como value
        """
        page_objects: Dict[str, List[str]] = {}

        selectors = self.extract_selectors()

        for selector in selectors:
            # Intentar identificar la página por el contexto
            page_name = self._identify_page_from_context(selector.context)

            if page_name not in page_objects:
                page_objects[page_name] = []

            page_objects[page_name].append(selector.value)

        return page_objects

    def _identify_page_from_context(self, context: str) -> str:
        """Identifica el nombre de la página desde el contexto."""
        context_lower = context.lower()

        # Mapeos comunes
        if "login" in context_lower:
            return "LoginPage"
        elif "customer" in context_lower:
            return "CustomerPage"
        elif "form" in context_lower or "formulario" in context_lower:
            return "FormPage"
        elif "nav" in context_lower or "menu" in context_lower:
            return "NavigationComponent"
        else:
            return "BasePage"

    def has_steps(self) -> bool:
        """Verifica si el test tiene steps definidos."""
        return len(self.steps) > 0

    def get_step_count(self) -> int:
        """Retorna el número de steps."""
        return len(self.steps)

    def __str__(self) -> str:
        """Representación en string del test file."""
        return (
            f"TestFile("
            f"path={self.path.name}, "
            f"name='{self.test_name}', "
            f"steps={self.get_step_count()}, "
            f"strategy='{self.strategy}'"
            f")"
        )
