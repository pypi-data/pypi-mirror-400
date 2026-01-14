# ==========================================
# MAKEFILE PARA HAKALAB FRAMEWORK v1.2.12
# Comandos simplificados para desarrollo y CI/CD
# ==========================================

# Variables por defecto
BROWSER ?= chromium
PARALLEL_WORKERS ?= 4
TEST_SUITE ?= smoke
HEADLESS ?= true
BASE_URL ?= https://example.com
DOCKER_IMAGE ?= hakalab-framework
REPORTS_PORT ?= 8080

# Colores para output
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

.PHONY: help install test docker clean reports serve

# ==========================================
# HELP - Mostrar comandos disponibles
# ==========================================
help: ## Mostrar esta ayuda
	@echo "$(GREEN)🚀 Hakalab Framework - Comandos Disponibles$(NC)"
	@echo ""
	@echo "$(YELLOW)📦 Instalación y Setup:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST) | grep -E "(install|setup|clean)"
	@echo ""
	@echo "$(YELLOW)🧪 Ejecución de Pruebas:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST) | grep -E "(test|smoke|regression|debug)"
	@echo ""
	@echo "$(YELLOW)🐳 Docker:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST) | grep -E "(docker|build|run)"
	@echo ""
	@echo "$(YELLOW)📊 Reportes:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST) | grep -E "(reports|serve)"
	@echo ""
	@echo "$(YELLOW)🔧 Variables de entorno disponibles:$(NC)"
	@echo "  BROWSER=$(BROWSER) (chromium|firefox|webkit)"
	@echo "  PARALLEL_WORKERS=$(PARALLEL_WORKERS)"
	@echo "  TEST_SUITE=$(TEST_SUITE) (smoke|regression|full|custom)"
	@echo "  HEADLESS=$(HEADLESS)"
	@echo "  BASE_URL=$(BASE_URL)"

# ==========================================
# INSTALACIÓN Y SETUP
# ==========================================
install: ## Instalar dependencias y configurar entorno
	@echo "$(GREEN)📦 Instalando Hakalab Framework...$(NC)"
	pip install --upgrade pip
	pip install -r requirements.txt
	python -m playwright install
	@echo "$(GREEN)✅ Instalación completada$(NC)"

setup: install ## Setup completo del proyecto
	@echo "$(GREEN)🔧 Configurando proyecto...$(NC)"
	cp .env.example .env
	mkdir -p html-reports screenshots logs downloads videos
	@echo "$(GREEN)✅ Proyecto configurado$(NC)"

install-dev: ## Instalar dependencias de desarrollo
	@echo "$(GREEN)🛠️  Instalando dependencias de desarrollo...$(NC)"
	pip install -r requirements.txt
	pip install -e .
	python -m playwright install
	@echo "$(GREEN)✅ Entorno de desarrollo listo$(NC)"

# ==========================================
# EJECUCIÓN DE PRUEBAS LOCALES
# ==========================================
test: ## Ejecutar todas las pruebas
	@echo "$(GREEN)🧪 Ejecutando todas las pruebas...$(NC)"
	BROWSER=$(BROWSER) HEADLESS=$(HEADLESS) behave --processes $(PARALLEL_WORKERS) --format html --outdir html-reports

smoke: ## Ejecutar smoke tests
	@echo "$(GREEN)💨 Ejecutando smoke tests...$(NC)"
	BROWSER=$(BROWSER) HEADLESS=$(HEADLESS) behave --processes $(PARALLEL_WORKERS) --tags @smoke --format html --outdir html-reports

regression: ## Ejecutar regression tests
	@echo "$(GREEN)🔄 Ejecutando regression tests...$(NC)"
	BROWSER=$(BROWSER) HEADLESS=$(HEADLESS) behave --processes $(PARALLEL_WORKERS) --tags @regression --format html --outdir html-reports

test-custom: ## Ejecutar tests con tags personalizados (usar TAGS=@mytag)
	@echo "$(GREEN)🏷️  Ejecutando tests personalizados: $(TAGS)$(NC)"
	BROWSER=$(BROWSER) HEADLESS=$(HEADLESS) behave --processes $(PARALLEL_WORKERS) --tags "$(TAGS)" --format html --outdir html-reports

test-multi-browser: ## Ejecutar tests en múltiples navegadores
	@echo "$(GREEN)🌐 Ejecutando tests en múltiples navegadores...$(NC)"
	@$(MAKE) test BROWSER=chromium &
	@$(MAKE) test BROWSER=firefox &
	@$(MAKE) test BROWSER=webkit &
	@wait
	@echo "$(GREEN)✅ Tests multi-browser completados$(NC)"

debug: ## Ejecutar en modo debug (sin headless)
	@echo "$(GREEN)🐛 Ejecutando en modo debug...$(NC)"
	BROWSER=$(BROWSER) HEADLESS=false SLOW_MO=1000 behave --no-capture --logging-level DEBUG

# ==========================================
# DOCKER COMMANDS
# ==========================================
docker-build: ## Construir imagen Docker
	@echo "$(GREEN)🐳 Construyendo imagen Docker...$(NC)"
	docker build -t $(DOCKER_IMAGE):latest \
		--build-arg PARALLEL_WORKERS=$(PARALLEL_WORKERS) \
		--build-arg BROWSER=$(BROWSER) .
	@echo "$(GREEN)✅ Imagen Docker construida$(NC)"

docker-test: docker-build ## Ejecutar tests en Docker
	@echo "$(GREEN)🐳 Ejecutando tests en Docker...$(NC)"
	docker run --rm \
		-v $(PWD)/features:/home/testuser/app/features:ro \
		-v $(PWD)/json_poms:/home/testuser/app/json_poms:ro \
		-v $(PWD)/html-reports:/home/testuser/app/html-reports \
		-v $(PWD)/screenshots:/home/testuser/app/screenshots \
		-e BROWSER=$(BROWSER) \
		-e PARALLEL_WORKERS=$(PARALLEL_WORKERS) \
		-e BASE_URL=$(BASE_URL) \
		$(DOCKER_IMAGE):latest

docker-smoke: docker-build ## Ejecutar smoke tests en Docker
	@echo "$(GREEN)🐳💨 Ejecutando smoke tests en Docker...$(NC)"
	docker run --rm \
		-v $(PWD)/features:/home/testuser/app/features:ro \
		-v $(PWD)/json_poms:/home/testuser/app/json_poms:ro \
		-v $(PWD)/html-reports:/home/testuser/app/html-reports \
		-v $(PWD)/screenshots:/home/testuser/app/screenshots \
		-e BROWSER=$(BROWSER) \
		-e PARALLEL_WORKERS=$(PARALLEL_WORKERS) \
		$(DOCKER_IMAGE):latest smoke

docker-regression: docker-build ## Ejecutar regression tests en Docker
	@echo "$(GREEN)🐳🔄 Ejecutando regression tests en Docker...$(NC)"
	docker run --rm \
		-v $(PWD)/features:/home/testuser/app/features:ro \
		-v $(PWD)/json_poms:/home/testuser/app/json_poms:ro \
		-v $(PWD)/html-reports:/home/testuser/app/html-reports \
		-v $(PWD)/screenshots:/home/testuser/app/screenshots \
		-v $(PWD)/videos:/home/testuser/app/videos \
		-e BROWSER=$(BROWSER) \
		-e PARALLEL_WORKERS=$(PARALLEL_WORKERS) \
		-e VIDEO_RECORDING=true \
		$(DOCKER_IMAGE):latest regression

docker-debug: docker-build ## Ejecutar Docker en modo debug interactivo
	@echo "$(GREEN)🐳🐛 Iniciando Docker en modo debug...$(NC)"
	docker run --rm -it \
		-v $(PWD):/home/testuser/app \
		-e BROWSER=$(BROWSER) \
		-e DEBUG_MODE=true \
		$(DOCKER_IMAGE):latest debug

# ==========================================
# DOCKER COMPOSE COMMANDS
# ==========================================
compose-up: ## Iniciar servicios con Docker Compose
	@echo "$(GREEN)🐳📦 Iniciando servicios con Docker Compose...$(NC)"
	docker-compose up --build

compose-smoke: ## Ejecutar smoke tests con Docker Compose
	@echo "$(GREEN)🐳💨 Ejecutando smoke tests con Docker Compose...$(NC)"
	docker-compose --profile smoke up --build

compose-regression: ## Ejecutar regression tests con Docker Compose
	@echo "$(GREEN)🐳🔄 Ejecutando regression tests con Docker Compose...$(NC)"
	docker-compose --profile regression up --build

compose-multi-browser: ## Ejecutar tests multi-browser con Docker Compose
	@echo "$(GREEN)🐳🌐 Ejecutando tests multi-browser con Docker Compose...$(NC)"
	docker-compose --profile multi-browser up --build

compose-reports: ## Iniciar servidor de reportes
	@echo "$(GREEN)🐳📊 Iniciando servidor de reportes...$(NC)"
	docker-compose --profile reports up -d
	@echo "$(YELLOW)📊 Reportes disponibles en: http://localhost:$(REPORTS_PORT)$(NC)"

compose-down: ## Detener todos los servicios
	@echo "$(GREEN)🐳⬇️  Deteniendo servicios...$(NC)"
	docker-compose down --remove-orphans

# ==========================================
# REPORTES Y VISUALIZACIÓN
# ==========================================
reports: ## Generar índice de reportes
	@echo "$(GREEN)📊 Generando índice de reportes...$(NC)"
	@if [ -d "html-reports" ]; then \
		echo "<!DOCTYPE html><html><head><title>Hakalab Framework - Reportes</title></head><body>" > html-reports/index.html; \
		echo "<h1>🚀 Hakalab Framework - Reportes de Pruebas</h1>" >> html-reports/index.html; \
		echo "<p>Generado: $$(date)</p><ul>" >> html-reports/index.html; \
		for file in html-reports/*.html; do \
			if [ "$$(basename $$file)" != "index.html" ]; then \
				echo "<li><a href='$$(basename $$file)'>$$(basename $$file)</a></li>" >> html-reports/index.html; \
			fi; \
		done; \
		echo "</ul></body></html>" >> html-reports/index.html; \
		echo "$(GREEN)✅ Índice de reportes generado$(NC)"; \
	else \
		echo "$(RED)❌ No se encontró directorio html-reports$(NC)"; \
	fi

serve: reports ## Servir reportes en servidor local
	@echo "$(GREEN)🌐 Iniciando servidor de reportes en puerto $(REPORTS_PORT)...$(NC)"
	@if command -v python3 >/dev/null 2>&1; then \
		cd html-reports && python3 -m http.server $(REPORTS_PORT); \
	elif command -v python >/dev/null 2>&1; then \
		cd html-reports && python -m http.server $(REPORTS_PORT); \
	else \
		echo "$(RED)❌ Python no encontrado. Instale Python para usar el servidor local$(NC)"; \
	fi

open-reports: ## Abrir reportes en navegador
	@echo "$(GREEN)🌐 Abriendo reportes en navegador...$(NC)"
	@if [ -f "html-reports/index.html" ]; then \
		if command -v xdg-open >/dev/null 2>&1; then \
			xdg-open html-reports/index.html; \
		elif command -v open >/dev/null 2>&1; then \
			open html-reports/index.html; \
		elif command -v start >/dev/null 2>&1; then \
			start html-reports/index.html; \
		else \
			echo "$(YELLOW)⚠️  No se pudo abrir automáticamente. Abra html-reports/index.html manualmente$(NC)"; \
		fi; \
	else \
		echo "$(RED)❌ No se encontraron reportes. Ejecute 'make test' primero$(NC)"; \
	fi

# ==========================================
# LIMPIEZA Y MANTENIMIENTO
# ==========================================
clean: ## Limpiar archivos generados
	@echo "$(GREEN)🧹 Limpiando archivos generados...$(NC)"
	rm -rf html-reports/* screenshots/* logs/* downloads/* videos/* test-results/*
	docker system prune -f
	@echo "$(GREEN)✅ Limpieza completada$(NC)"

clean-docker: ## Limpiar imágenes Docker
	@echo "$(GREEN)🧹🐳 Limpiando imágenes Docker...$(NC)"
	docker rmi $(DOCKER_IMAGE):latest || true
	docker system prune -f
	@echo "$(GREEN)✅ Imágenes Docker limpiadas$(NC)"

clean-all: clean clean-docker ## Limpieza completa
	@echo "$(GREEN)🧹💥 Limpieza completa realizada$(NC)"

# ==========================================
# UTILIDADES DE DESARROLLO
# ==========================================
check-env: ## Verificar configuración del entorno
	@echo "$(GREEN)🔍 Verificando configuración del entorno...$(NC)"
	@echo "Python: $$(python --version 2>/dev/null || echo 'No instalado')"
	@echo "Pip: $$(pip --version 2>/dev/null || echo 'No instalado')"
	@echo "Playwright: $$(python -c 'import playwright; print(playwright.__version__)' 2>/dev/null || echo 'No instalado')"
	@echo "Docker: $$(docker --version 2>/dev/null || echo 'No instalado')"
	@echo "Docker Compose: $$(docker-compose --version 2>/dev/null || echo 'No instalado')"

lint: ## Ejecutar linting del código
	@echo "$(GREEN)🔍 Ejecutando linting...$(NC)"
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 hakalab_framework/ --max-line-length=120; \
	else \
		echo "$(YELLOW)⚠️  flake8 no instalado. Instale con: pip install flake8$(NC)"; \
	fi

format: ## Formatear código con black
	@echo "$(GREEN)🎨 Formateando código...$(NC)"
	@if command -v black >/dev/null 2>&1; then \
		black hakalab_framework/ --line-length=120; \
	else \
		echo "$(YELLOW)⚠️  black no instalado. Instale con: pip install black$(NC)"; \
	fi

# ==========================================
# CI/CD HELPERS
# ==========================================
ci-test: ## Ejecutar tests para CI/CD
	@echo "$(GREEN)🚀 Ejecutando tests para CI/CD...$(NC)"
	BROWSER=$(BROWSER) HEADLESS=true behave --processes $(PARALLEL_WORKERS) --format html --outdir html-reports --junit --junit-directory test-results

ci-smoke: ## Ejecutar smoke tests para CI/CD
	@echo "$(GREEN)🚀💨 Ejecutando smoke tests para CI/CD...$(NC)"
	BROWSER=$(BROWSER) HEADLESS=true behave --processes $(PARALLEL_WORKERS) --tags @smoke --format html --outdir html-reports --junit --junit-directory test-results

# ==========================================
# SHORTCUTS ÚTILES
# ==========================================
quick-test: smoke ## Alias para smoke tests
quick-smoke: smoke ## Alias para smoke tests
full-test: regression ## Alias para regression tests
dev-test: debug ## Alias para debug mode