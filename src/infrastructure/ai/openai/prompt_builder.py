"""Builder de prompts para OpenAI."""

from typing import List, Optional

from src.domain.model.test_file import TestFile


class PromptBuilder:
    """
    Constructor de prompts para diferentes tipos de generación.

    Centraliza la lógica de construcción de prompts siguiendo
    patrones de prompt engineering.
    """

    SYSTEM_PROMPT_POM = """Eres un experto en Page Object Model (POM) para Playwright con TypeScript.

Tus responsabilidades:
- Diseñar estructuras POM claras y mantenibles
- Seguir best practices de Playwright
- Usar selectores data-testid cuando sea posible
- Crear métodos reutilizables y bien nombrados
- Documentar claramente cada componente"""

    SYSTEM_PROMPT_CUCUMBER = """Eres un experto en testing BDD con Cucumber y Playwright.

Tus responsabilidades:
- Escribir features con sintaxis Gherkin clara
- Crear step definitions TypeScript bien estructuradas
- Integrar Cucumber con Playwright correctamente
- Seguir patrones BDD estándar
- Usar World context apropiadamente"""

    SYSTEM_PROMPT_PLAYWRIGHT = """Eres un experto en testing E2E con Playwright y TypeScript.

Tus responsabilidades:
- Refactorizar tests para usar POM
- Mantener estructura BDD con test.step()
- Crear fixtures y data providers eficientes
- Organizar tests de forma modular
- Aplicar best practices de Playwright"""

    @staticmethod
    def build_pom_generation_prompt(
        test_files: List[TestFile], existing_pom: Optional[str] = None
    ) -> str:
        """
        Construye prompt para generar POM.md y POM-components.md.

        Args:
            test_files: Lista de tests a analizar
            existing_pom: Contenido de POM.md existente (opcional)

        Returns:
            Prompt completo para OpenAI
        """
        # Extraer información de los tests
        test_info = []
        for test in test_files:
            selectors = test.extract_selectors()
            selector_summary = "\n".join(
                f"  - {sel.action}: {sel.value} ({sel.element_type})"
                for sel in selectors[:10]  # Limitar a 10 por test
            )

            test_info.append(
                f"""
## Test: {test.test_name}
**Objetivo:** {test.objective}
**Strategy:** {test.strategy}

**Selectores encontrados:**
{selector_summary}
"""
            )

        tests_section = "\n".join(test_info)

        existing_pom_section = ""
        if existing_pom:
            existing_pom_section = f"""
## POM Existente

Actualiza y mejora esta estructura existente:

```markdown
{existing_pom[:2000]}
```
"""

        prompt = f"""Analiza los siguientes tests Playwright y genera documentación POM.

{tests_section}

{existing_pom_section}

## Genera DOS documentos markdown:

### 1. POM.md
Estructura de directorios y métodos del POM:
- Árbol de carpetas (tests/pages/, tests/components/)
- Lista de Page Objects con métodos públicos
- Convenciones de naming
- Diagrama de dependencias

### 2. POM-components.md
Implementaciones detalladas en TypeScript:
- Código completo de cada Page Object
- Path recomendado para cada archivo
- Explicación de selectores y por qué se eligieron
- Ejemplos de uso de cada método
- Imports necesarios

**Formato de respuesta:**

```markdown
# POM.md

[Contenido de POM.md aquí]

---

# POM-components.md

[Contenido de POM-components.md aquí]
```

**Requisitos:**
- Usa selectores data-testid cuando sea posible
- Métodos deben retornar Page Objects (fluent interface)
- Agrupa lógicamente por páginas/secciones
- Incluye tipos TypeScript estrictos
- Documenta cada método con JSDoc"""

        return prompt

    @staticmethod
    def build_cucumber_generation_prompt(test_files: List[TestFile]) -> str:
        """Construye prompt para generar cucumber.md."""
        test_examples = []

        for test in test_files[:2]:  # Limitar a 2 ejemplos
            test_examples.append(
                f"""
## Ejemplo de Test

```typescript
// {test.test_name}
// Objetivo: {test.objective}

{test.content[:800]}...
```
"""
            )

        examples_section = "\n".join(test_examples)

        prompt = f"""Convierte estos tests Playwright a Cucumber + Playwright.

{examples_section}

## Genera cucumber.md con:

### 1. Feature Files (.feature)
- Sintaxis Gherkin completa
- Scenarios bien estructurados
- Background cuando aplique
- Examples para data-driven tests

### 2. Step Definitions (.ts)
- Implementación usando POM
- World context configurado
- Hooks (Before/After) necesarios
- Manejo de errores

### 3. Configuración
- cucumber.config.ts
- Integración con Playwright
- Scripts package.json

### 4. Guía de Uso
- Cómo ejecutar tests
- Cómo añadir nuevos scenarios
- Best practices

**Formato:** Markdown con secciones claras y bloques de código ejecutables."""

        return prompt

    @staticmethod
    def build_playwright_refactor_prompt(test_files: List[TestFile]) -> str:
        """Construye prompt para generar playwright.md."""
        test_examples = []

        for test in test_files[:2]:
            test_examples.append(
                f"""
## Test Original

```typescript
// {test.test_name}
{test.content[:800]}...
```
"""
            )

        examples_section = "\n".join(test_examples)

        prompt = f"""Refactoriza estos tests Playwright para usar POM.

{examples_section}

## Genera playwright.md con:

### 1. Tests Refactorizados
- Usa Page Objects en lugar de selectores directos
- Mantiene test.step() con Gherkin
- Imports correctos de Page Objects
- Código limpio y DRY

### 2. Data Providers (Fixtures)
- Fixtures para datos de test
- test.describe.configure() para paralelización
- Ejemplos de data-driven tests

### 3. Organización
- Agrupación por módulos/features
- Reutilización de steps comunes
- Hooks compartidos (beforeEach, afterEach)

### 4. Ejemplos de Uso
- Cómo ejecutar tests
- Cómo añadir nuevos tests
- Patrones recomendados

**Formato:** Markdown con código TypeScript completo y ejecutable.
**Objetivo:** Tests mantenibles y escalables usando POM."""

        return prompt
