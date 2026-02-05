"""Builder de prompts para OpenAI."""

from typing import List, Optional

from src.domain.model.test_file import TestFile


class PromptBuilder:
    """
    Constructor de prompts para diferentes tipos de generación.

    Centraliza la lógica de construcción de prompts siguiendo
    patrones de prompt engineering.
    """

    SYSTEM_PROMPT_POM = """Eres un experto en Page Object Model (POM) para \
Playwright con TypeScript.

REGLAS CRÍTICAS:
1. SOLO usa selectores que aparecen EXACTAMENTE en los tests proporcionados
2. NO inventes, modifiques ni "mejores" selectores
3. Los tests son código VALIDADO y FUNCIONAL - replica su lógica exactamente
4. NO asumas elementos que no están en los tests
5. Si un selector es largo o complejo, úsalo tal cual está

Tus responsabilidades:
- Diseñar estructuras POM claras y mantenibles
- Extraer selectores EXACTOS de los tests
- Seguir best practices de Playwright
- Crear métodos reutilizables y bien nombrados
- Documentar claramente cada componente

IMPORTANTE: Tu trabajo es DOCUMENTAR lo que existe, NO inventar mejoras."""

    SYSTEM_PROMPT_CUCUMBER = """Eres un experto en testing BDD con Cucumber y Playwright.

REGLAS CRÍTICAS:
1. SOLO usa selectores de los tests originales - NO inventes nuevos
2. Replica EXACTAMENTE la lógica de los tests validados
3. NO modifiques ni "mejores" los selectores existentes
4. Los tests funcionan - respeta su implementación

Tus responsabilidades:
- Escribir features con sintaxis Gherkin clara
- Crear step definitions TypeScript usando POM
- Integrar Cucumber con Playwright correctamente
- Seguir patrones BDD estándar
- Usar World context apropiadamente"""

    SYSTEM_PROMPT_PLAYWRIGHT = """Eres un experto en testing E2E con Playwright y TypeScript.

REGLAS CRÍTICAS:
1. SOLO refactoriza para usar POM - NO cambies selectores
2. Usa EXACTAMENTE los mismos selectores de los tests originales
3. Los tests son FUNCIONALES - no los "mejores", solo organízalos
4. NO inventes nuevos elementos ni modifices selectores

Tus responsabilidades:
- Refactorizar tests para usar POM (sin cambiar selectores)
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

        prompt = f"""Analiza los siguientes tests Playwright VALIDADOS Y FUNCIONALES.

{tests_section}

{existing_pom_section}

⚠️ RESTRICCIONES CRÍTICAS:
1. USA SOLO los selectores que aparecen en los tests - NO inventes nuevos
2. NO modifiques ni "mejores" los selectores existentes
3. Si un selector usa text(), xpath, o css complejo - úsalo TAL CUAL
4. Estos tests FUNCIONAN - replica su lógica exactamente
5. NO asumas elementos que no están explícitos en los tests

## Genera DOS documentos markdown:

### 1. POM.md - DEBE CONTENER:
**Estructura del archivo:**
```
# Page Object Model - [Nombre del Proyecto]

## 📁 Estructura de Directorios
[Árbol de carpetas: tests/pages/, tests/components/, tests/fixtures/]

## 📄 Page Objects

### LoginPage
**Path:** tests/pages/LoginPage.ts
**Métodos:**
- fillUsername(username: string): LoginPage
- fillPassword(password: string): LoginPage
- clickLogin(): Promise<void>
[etc...]

[Repetir para cada Page Object]

## 🔧 Convenciones
[Naming, retorno de métodos, tipos]

## 🗺️ Diagrama de Dependencias
[Qué Page Objects usan otros]
```

### 2. POM-components.md - DEBE CONTENER:
**Estructura del archivo:**
```
# Implementaciones POM

## LoginPage

**Path:** `tests/pages/LoginPage.ts`

**Código:**
\`\`\`typescript
import {{ Page }} from '@playwright/test';

export class LoginPage {{
  constructor(private page: Page) {{}}

  async fillUsername(username: string) {{
    // Selector EXACTO del test original:
    await this.page.locator('input[name="uid"]').fill(username);
    return this;
  }}
  // ... más métodos con selectores EXACTOS
}}
\`\`\`

**Selectores Utilizados:**
- `input[name="uid"]` - Campo username (del test original línea X)
- [lista todos los selectores EXACTOS con su origen]

**Uso:**
\`\`\`typescript
const loginPage = new LoginPage(page);
await loginPage.fillUsername('user').fillPassword('pass');
\`\`\`

[Repetir sección completa para cada Page Object]
```

**Formato de respuesta:**

```markdown
# POM.md

[Contenido COMPLETO de POM.md aquí]

---

# POM-components.md

[Contenido COMPLETO de POM-components.md aquí]
```

**Requisitos OBLIGATORIOS:**
- Usa EXACTAMENTE los selectores de los tests (no inventes ni modifiques)
- Si selector es text() o xpath - cópialo tal cual
- Métodos retornan Page Objects (fluent interface)
- Incluye tipos TypeScript estrictos
- Documenta ORIGEN de cada selector (del test X)"""

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

        prompt = f"""Convierte estos tests Playwright VALIDADOS a Cucumber + Playwright.

{examples_section}

⚠️ RESTRICCIONES CRÍTICAS:
1. USA los mismos selectores de los tests - NO inventes ni modifiques
2. Replica EXACTAMENTE las acciones de los tests originales
3. NO asumas elementos adicionales
4. Los tests funcionan - solo convierte el formato, no la lógica

## Genera cucumber.md con ESTAS SECCIONES:

### 1. Feature Files (.feature)
```gherkin
# login.feature
Feature: Login funcionalidad
  [Scenarios basados en tests originales]
```

### 2. Step Definitions (.ts)
```typescript
// login.steps.ts
import {{ Given, When, Then }} from '@cucumber/cucumber';
import {{ LoginPage }} from '../pages/LoginPage';

Given('usuario está en login', async function() {{
  // Usa Page Objects con selectores EXACTOS de tests originales
}});
```

### 3. Configuración
```typescript
// cucumber.config.ts
[Config completa]
```

```json
// package.json scripts
[Scripts para ejecutar]
```

### 4. Guía de Uso
- Comandos de ejecución
- Estructura de archivos
- Cómo añadir scenarios

**IMPORTANTE:** Step definitions DEBEN usar Page Objects con selectores EXACTOS \
del test original."""

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

        prompt = f"""Refactoriza estos tests Playwright FUNCIONALES para usar POM.

{examples_section}

⚠️ RESTRICCIONES CRÍTICAS:
1. SOLO cambia selectores directos por llamadas a Page Objects
2. Los Page Objects DEBEN usar los mismos selectores exactos
3. NO modifiques la lógica ni los selectores originales
4. Mantiene TODAS las aserciones y validaciones tal cual
5. Estos tests FUNCIONAN - solo organízalos con POM

## Genera playwright.md con ESTAS SECCIONES:

### 1. Tests Refactorizados
```typescript
import {{ test, expect }} from '@playwright/test';
import {{ LoginPage }} from './pages/LoginPage';

test('Login con credenciales válidas', async ({{ page }}) => {{
  const loginPage = new LoginPage(page);

  await test.step('Given usuario en login', async () => {{
    await page.goto('/login');
  }});

  await test.step('When ingresa credenciales válidas', async () => {{
    // Usa Page Object con selectores EXACTOS del test original
    await loginPage.fillUsername('user');
    await loginPage.fillPassword('pass');
    await loginPage.clickLogin();
  }});

  await test.step('Then ve dashboard', async () => {{
    // Mismas aserciones del test original
    await expect(page).toHaveURL(/dashboard/);
  }});
}});
```

### 2. Data Providers (Fixtures)
```typescript
// fixtures/test-data.ts
export const loginData = {{ ... }};
```

### 3. Organización de Tests
- Agrupación por features
- Hooks compartidos
- Reutilización de pasos comunes

### 4. Guía de Ejecución
- Comandos para ejecutar
- Estructura de archivos
- Cómo añadir tests nuevos

**CRÍTICO:** El código refactorizado debe hacer EXACTAMENTE lo mismo que el \
original, solo usando POM."""

        return prompt
