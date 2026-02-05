# 🤖 POM-PPIA

**Generador de POM y tests Cucumber/Playwright desde tests declarativos usando Python + OpenAI**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## 📋 Descripción

POM-PPIA transforma tests Playwright declarativos generados por [PPIA](https://github.com/joseguillermomoreu-gif/pom-ppia) en:

- ✅ **POM.md** - Estructura de Page Object Model con directorios y métodos
- ✅ **POM-components.md** - Implementaciones TypeScript de Page Objects
- ✅ **cucumber.md** - Tests con Cucumber + Gherkin
- ✅ **playwright.md** - Tests refactorizados con POM (sin Cucumber)

Todo esto usando **OpenAI GPT-4 mini** para análisis y generación inteligente.

---

## 🎯 Características

- 🏗️ **Arquitectura Hexagonal** - Domain, Application, Infrastructure
- 🎨 **SOLID Principles** - Código limpio y mantenible
- 🔌 **Puertos y Adaptadores** - Fácil extensión (nuevos LLMs, outputs)
- 🧪 **Type-safe** - Type hints completos + mypy strict
- 🖥️ **CLI Interactiva** - Selector de tests con Rich UI
- ⚙️ **Configurable** - YAML + .env para máxima flexibilidad
- 🚫 **Filtro MCP** - Excluye automáticamente tests con MCP sequences

---

## 🚀 Instalación

### Requisitos

- Python 3.12+
- Poetry (recomendado) o pip

### Setup

```bash
# Clonar repositorio
git clone https://github.com/joseguillermomoreu-gif/pom-ppia.git
cd pom-ppia

# Instalar con Poetry
poetry install

# O con pip
pip install -e .

# Configurar variables de entorno
cp .env.example .env
# Editar .env y añadir tu OPENAI_API_KEY
```

---

## 📖 Uso

### CLI Interactiva

```bash
poetry run python -m src.infrastructure.cli.main \
  --input /path/to/playwright/tests \
  --output ./output
```

**Flujo interactivo:**

```
🔍 Escaneando directorio: /path/to/tests
✓ Encontrados 6 archivos de test
❌ Excluidos 2 tests con MCP sequences

📋 Tests disponibles:
  1. test-strategy1-login-functionality.spec.ts
  2. test-strategy2-form-validation.spec.ts
  3. test-strategy3-navigation.spec.ts

¿Qué deseas procesar?
  [a] Todos los tests
  [n] Número específico (ej: 1,3)
  [q] Salir

Selección: 1,2

✓ Seleccionados: 2 tests

🤖 Procesando con OpenAI (gpt-4o-mini)...

  [1/4] Generando POM.md .......................... ✓ (12.3s)
  [2/4] Generando POM-components.md ............... ✓ (18.7s)
  [3/4] Generando cucumber.md ..................... ✓ (15.2s)
  [4/4] Generando playwright.md ................... ✓ (14.1s)

✅ Generación completada

📁 Archivos generados en: ./output/
  - POM.md
  - POM-components.md
  - cucumber.md
  - playwright.md

💰 Coste estimado: $0.023 USD
⏱️  Tiempo total: 60.3s
```

### Con POM Existente

```bash
poetry run python -m src.infrastructure.cli.main \
  --input /path/to/tests \
  --pom existing-pom.md \
  --output ./output
```

---

## 🏗️ Arquitectura

### Estructura del Proyecto

```
pom-ppia/
├── src/
│   ├── domain/          # Lógica de negocio pura
│   ├── application/     # Casos de uso
│   └── infrastructure/  # Adaptadores (OpenAI, CLI, FS)
├── tests/
├── config/
└── output/
```

### Capas Hexagonales

```
CLI → Application (Use Cases) → Domain ← Infrastructure
                                    ↓
                              Puertos (Interfaces)
                                    ↓
                    ┌───────────────┼───────────────┐
                    ↓               ↓               ↓
            FileRepository    OpenAIService   MarkdownGenerator
```

---

## 🧪 Testing

```bash
# Ejecutar todos los tests
poetry run pytest -v

# Con cobertura
poetry run pytest --cov=src --cov-report=html

# Type checking
poetry run mypy src/

# Linting
poetry run ruff check src/

# Formateo
poetry run black src/
```

---

## ⚙️ Configuración

### Variables de Entorno (.env)

```bash
OPENAI_API_KEY=sk-...
DEFAULT_MODEL=gpt-4o-mini
TEMPERATURE=0.7
```

### Configuración de Modelos (config/llm-providers.yaml)

```yaml
providers:
  openai:
    default_model: "gpt-4o-mini"
    models:
      - name: "gpt-4o-mini"
        cost_per_1k_input: 0.00015
```

---

## 🚫 Filtrado de Tests MCP

Los tests que usan `MCPUse.executeSequence()` son **automáticamente excluidos**:

```typescript
// ❌ Este test NO será procesado
import { MCPUse } from '@ppia/mcp/MCPUse';

test('Test with MCP', async ({ page }) => {
  const actions: MCPAction[] = [...]
  await MCPUse.executeSequence(page, actions);
});

// ✅ Este test SÍ será procesado
test('Test without MCP', async ({ page }) => {
  await page.locator('input').fill('text');
  await page.click('button');
});
```

---

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama feature (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'Add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request a `develop`

### Gitflow

- `master` - Producción (releases)
- `develop` - Desarrollo
- `feature/*` - Nuevas features

---

## 📄 Licencia

MIT License - ver [LICENSE](LICENSE) para más detalles.

---

## 🙏 Agradecimientos

- [PPIA](https://github.com/joseguillermomoreu-gif/pom-ppia) - Generador de tests Playwright
- [OpenAI](https://openai.com) - GPT-4 para análisis inteligente
- Comunidad de Playwright y Cucumber

---

## 📞 Contacto

**Autor:** jgmoreu

**Repository:** [https://github.com/joseguillermomoreu-gif/pom-ppia](https://github.com/joseguillermomoreu-gif/pom-ppia)

---

⭐ Si te resulta útil, considera darle una estrella al repo!
