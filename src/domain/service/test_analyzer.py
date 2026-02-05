"""Domain Service: Analizador de tests."""

import re
from typing import Dict, List

from src.domain.model.pom_structure import Component, PageObject, POMStructure
from src.domain.model.selector import Selector
from src.domain.model.test_file import TestFile
from src.domain.model.test_step import TestStep


class TestAnalyzer:
    """
    Servicio de dominio para analizar tests y extraer información.

    Este servicio encapsula lógica de negocio compleja que no pertenece
    a una sola entidad.
    """

    def analyze_tests(self, test_files: List[TestFile]) -> Dict[str, any]:
        """
        Analiza múltiples tests y extrae información agregada.

        Args:
            test_files: Lista de TestFile a analizar

        Returns:
            Diccionario con análisis completo:
                - all_selectors: Lista de todos los selectores
                - unique_selectors: Set de selectores únicos
                - selector_frequency: Frecuencia de cada selector
                - page_objects: Estructura POM propuesta
                - total_steps: Total de steps
                - step_types: Distribución de tipos de steps
        """
        all_selectors: List[Selector] = []
        all_steps: List[TestStep] = []
        page_objects_data: Dict[str, List[str]] = {}

        for test_file in test_files:
            # Extraer selectores
            selectors = test_file.extract_selectors()
            all_selectors.extend(selectors)

            # Recopilar steps
            all_steps.extend(test_file.steps)

            # Identificar page objects
            page_objs = test_file.get_page_objects()
            for page_name, selectors_list in page_objs.items():
                if page_name not in page_objects_data:
                    page_objects_data[page_name] = []
                page_objects_data[page_name].extend(selectors_list)

        # Calcular estadísticas
        unique_selectors = set(sel.value for sel in all_selectors)
        selector_frequency = self._calculate_frequency(
            [sel.value for sel in all_selectors]
        )
        step_types = self._calculate_step_types(all_steps)

        # Generar estructura POM
        pom_structure = self._generate_pom_structure(page_objects_data)

        return {
            "all_selectors": all_selectors,
            "unique_selectors": unique_selectors,
            "selector_frequency": selector_frequency,
            "page_objects": pom_structure,
            "total_steps": len(all_steps),
            "step_types": step_types,
            "test_count": len(test_files),
        }

    def extract_steps_from_content(self, content: str) -> List[TestStep]:
        """
        Extrae test steps desde el contenido de un test.

        Args:
            content: Contenido del archivo de test

        Returns:
            Lista de TestStep extraídos
        """
        steps: List[TestStep] = []

        # Patrón para detectar test.step()
        step_pattern = r"await\s+test\.step\(['\"]([^'\"]+)['\"]\s*,\s*async"
        matches = re.finditer(step_pattern, content)

        for match in matches:
            step_description = match.group(1)

            # Determinar tipo de step desde la descripción
            step_type = self._infer_step_type(step_description)

            # Extraer acciones del bloque del step
            # (simplificado - en una implementación real sería más complejo)
            actions = self._extract_actions_from_step(content, match.start())

            # Crear selectores vacíos por ahora
            # (se llenarían en un análisis más profundo)
            selectors: List[Selector] = []

            step = TestStep(
                step_type=step_type,
                description=step_description,
                actions=actions,
                selectors=selectors,
            )

            steps.append(step)

        return steps

    def _infer_step_type(self, description: str) -> str:
        """Infiere el tipo de step desde su descripción."""
        desc_lower = description.lower()

        if desc_lower.startswith("given"):
            return "given"
        elif desc_lower.startswith("when"):
            return "when"
        elif desc_lower.startswith("then"):
            return "then"
        elif desc_lower.startswith("and"):
            return "and"
        else:
            # Por defecto, clasificar por palabras clave
            if any(
                word in desc_lower
                for word in ["navega", "abre", "accede", "se encuentra"]
            ):
                return "given"
            elif any(
                word in desc_lower
                for word in ["pulsa", "hace click", "rellena", "selecciona"]
            ):
                return "when"
            elif any(
                word in desc_lower for word in ["verifica", "comprueba", "debe"]
            ):
                return "then"
            else:
                return "and"

    def _extract_actions_from_step(self, content: str, start_pos: int) -> List[str]:
        """Extrae las acciones realizadas en un step."""
        actions: List[str] = []

        # Buscar en un chunk limitado después del step
        chunk = content[start_pos : start_pos + 500]

        action_patterns = [
            r"\.fill\(",
            r"\.click\(",
            r"\.check\(",
            r"\.select\(",
            r"expect\(",
            r"\.goto\(",
        ]

        for pattern in action_patterns:
            if re.search(pattern, chunk):
                action_name = pattern.replace(r"\(", "").replace(".", "").replace("\\", "")
                actions.append(action_name)

        return actions

    def _calculate_frequency(self, items: List[str]) -> Dict[str, int]:
        """Calcula la frecuencia de aparición de items."""
        frequency: Dict[str, int] = {}

        for item in items:
            frequency[item] = frequency.get(item, 0) + 1

        # Ordenar por frecuencia descendente
        return dict(sorted(frequency.items(), key=lambda x: x[1], reverse=True))

    def _calculate_step_types(self, steps: List[TestStep]) -> Dict[str, int]:
        """Calcula la distribución de tipos de steps."""
        step_types: Dict[str, int] = {
            "given": 0,
            "when": 0,
            "then": 0,
            "and": 0,
        }

        for step in steps:
            step_types[step.step_type] = step_types.get(step.step_type, 0) + 1

        return step_types

    def _generate_pom_structure(
        self, page_objects_data: Dict[str, List[str]]
    ) -> POMStructure:
        """
        Genera estructura POM desde los datos de page objects.

        Args:
            page_objects_data: Diccionario con nombre de página y selectores

        Returns:
            Estructura POMStructure completa
        """
        pages: Dict[str, PageObject] = {}
        components: Dict[str, Component] = {}

        for page_name, selectors in page_objects_data.items():
            # Determinar si es un Component o un Page
            if "Component" in page_name:
                # Es un componente
                component = Component(
                    name=page_name,
                    methods=self._generate_methods_from_selectors(selectors),
                    path=f"tests/components/{self._to_filename(page_name)}.ts",
                )
                components[page_name] = component
            else:
                # Es una página
                page = PageObject(
                    name=page_name,
                    methods=self._generate_methods_from_selectors(selectors),
                    selectors=selectors,
                    path=f"tests/pages/{self._to_filename(page_name)}.ts",
                )
                pages[page_name] = page

        return POMStructure(pages=pages, components=components, base_path="tests")

    def _generate_methods_from_selectors(self, selectors: List[str]) -> List[str]:
        """Genera nombres de métodos desde selectores."""
        methods: List[str] = []

        # Simplificado - generar métodos genéricos
        if any("login" in sel.lower() for sel in selectors):
            methods.append("login(username: string, password: string): Promise<void>")

        if any("name" in sel.lower() for sel in selectors):
            methods.append("fillName(name: string): Promise<void>")

        if any("submit" in sel.lower() or "button" in sel.lower() for sel in selectors):
            methods.append("submit(): Promise<void>")

        if any("reset" in sel.lower() for sel in selectors):
            methods.append("reset(): Promise<void>")

        # Método genérico por defecto
        if not methods:
            methods.append("interact(): Promise<void>")

        return methods

    def _to_filename(self, page_name: str) -> str:
        """Convierte nombre de Page/Component a filename."""
        # LoginPage → login.page
        # FormComponent → form.component
        name = page_name.replace("Page", "").replace("Component", "")
        name = re.sub(r"(?<!^)(?=[A-Z])", "-", name).lower()

        if "component" in page_name.lower():
            return f"{name}.component"
        else:
            return f"{name}.page"
