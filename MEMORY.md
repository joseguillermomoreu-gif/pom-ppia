# Skills Configurados - Proyecto Python + IA

Auto-generado por Claude Code el 2026-02-05

## Skills Activos
- python.md - Guía PHP → Python con equivalencias y patrones
- llms.md - Large Language Models (OpenAI, Claude, Gemini)
- openai.md - OpenAI API patterns con Python
- clean-code.md - Código limpio y mantenible
- arquitectura-hexagonal.md - Ports & Adapters, DDD
- solid.md - Principios SOLID de diseño OOP

## Skills Disponibles (no cargados)
- php-symfony.md
- laravel.md
- playwright.md
- pom.md
- typescript.md
- react.md
- cucumber.md
- bash-scripts.md
- phpstan.md
- swagger.md
- twig.md
- volt.md
- github-actions.md
- gitlab-ci.md

## Notas del Proyecto

### Stack Tecnológico
- **Lenguaje:** Python 3.12+
- **Enfoque:** Desarrollo de aplicaciones con IA/LLMs
- **Arquitectura:** Hexagonal (Ports & Adapters)
- **Principios:** SOLID, Clean Code

### Estructura Sugerida
```
src/
├── domain/          # Lógica de negocio pura
├── application/     # Casos de uso
├── infrastructure/  # Adaptadores (APIs, DB, etc.)
└── config/          # Configuración
```

### Comandos Útiles
```bash
# Gestión de dependencias
poetry install           # Instalar dependencias
poetry add <package>     # Añadir paquete

# Testing
pytest -v               # Ejecutar tests

# Type checking
mypy src/              # Verificar tipos

# Linting
ruff check             # Verificar código
```

## Contexto
Proyecto nuevo de Python enfocado en desarrollo con LLMs siguiendo buenas prácticas de arquitectura limpia.

---
💡 Para modificar: "carga [skill]" o "remueve [skill]"
*Última actualización: 2026-02-05 11:09*
