.PHONY: help install build up down shell run logs clean

# Colores para output
GREEN  := \033[0;32m
YELLOW := \033[0;33m
NC     := \033[0m # No Color

help: ## Muestra esta ayuda
	@echo "$(GREEN)POM-PPIA - Comandos disponibles:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""

install: ## Construye la imagen Docker (primera vez)
	@echo "$(GREEN)📦 Construyendo imagen Docker...$(NC)"
	docker-compose build
	@echo "$(GREEN)✅ Imagen construida correctamente$(NC)"
	@echo ""
	@echo "$(YELLOW)⚠️  IMPORTANTE: Configura tu API key de OpenAI en .env$(NC)"
	@echo "$(YELLOW)   Edita .env y añade: OPENAI_API_KEY=sk-tu-key$(NC)"
	@echo ""

build: install ## Alias de install

up: ## Levanta el contenedor en background
	@echo "$(GREEN)🚀 Levantando contenedor...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✅ Contenedor levantado$(NC)"
	@echo ""
	@echo "$(YELLOW)Usa 'make shell' para conectarte$(NC)"

down: ## Detiene y elimina el contenedor
	@echo "$(YELLOW)⬇️  Deteniendo contenedor...$(NC)"
	docker-compose down
	@echo "$(GREEN)✅ Contenedor detenido$(NC)"

shell: ## Conecta al contenedor (shell interactivo)
	@echo "$(GREEN)🐚 Conectando al contenedor...$(NC)"
	@docker-compose exec pom-ppia /bin/bash || \
		(echo "$(YELLOW)Contenedor no está corriendo. Levantándolo...$(NC)" && \
		 docker-compose up -d && \
		 docker-compose exec pom-ppia /bin/bash)

run: ## Ejecuta el programa en modo interactivo
	@echo "$(GREEN)🤖 Ejecutando POM-PPIA...$(NC)"
	docker-compose exec pom-ppia python3 -m src.infrastructure.cli.main --input /tests

run-all: ## Ejecuta procesando TODOS los tests (no interactivo)
	@echo "$(GREEN)🤖 Ejecutando POM-PPIA (todos los tests)...$(NC)"
	docker-compose exec pom-ppia python3 -m src.infrastructure.cli.main --input /tests --non-interactive

logs: ## Muestra logs del contenedor
	docker-compose logs -f pom-ppia

clean: ## Limpia archivos generados y contenedores
	@echo "$(YELLOW)🧹 Limpiando...$(NC)"
	rm -rf output/*.md
	docker-compose down -v
	@echo "$(GREEN)✅ Limpieza completa$(NC)"

restart: down up ## Reinicia el contenedor

rebuild: ## Reconstruye imagen y reinicia (para desarrollo)
	@echo "$(YELLOW)🔄 Reconstruyendo imagen...$(NC)"
	@$(MAKE) down
	@echo "$(GREEN)📦 Construyendo imagen sin cache...$(NC)"
	@docker-compose build --no-cache
	@$(MAKE) up
	@echo "$(GREEN)✅ Imagen reconstruida y contenedor levantado$(NC)"
	@echo ""
	@echo "$(YELLOW)Usa 'make shell' para conectarte$(NC)"

status: ## Muestra estado del contenedor
	@echo "$(GREEN)📊 Estado del contenedor:$(NC)"
	@docker-compose ps

# Comandos de desarrollo
test: ## Ejecuta tests (cuando estén implementados)
	docker-compose exec pom-ppia pytest -v

lint: ## Ejecuta linting
	docker-compose exec pom-ppia ruff check src/

format: ## Formatea el código
	docker-compose exec pom-ppia black src/

typecheck: ## Verifica tipos con mypy
	docker-compose exec pom-ppia mypy src/
