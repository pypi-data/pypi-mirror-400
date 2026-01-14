# Guía de Desarrollo - Haka Framework

## Configuración del Entorno de Desarrollo

### Prerrequisitos

- Python 3.8 o superior
- Git
- Editor de código (VS Code recomendado)
- Node.js (para Allure CLI, opcional)

### Configuración Inicial

```bash
# Clonar el repositorio
git clone https://github.com/pipefariashaka/hakalab-framework.git
cd hakalab-framework

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
# o
venv\Scripts\activate     # Windows

# Instalar dependencias de desarrollo
pip install -e ".[dev]"

# Instalar navegadores de Playwright
python -m playwright install

# Configurar pre-commit hooks
pre-commit install
```

## Estructura del Código

### Organización de Módulos

```
hakalab_framework/
├── __init__.py                 # Inicialización del paquete
├── cli.py                      # Interfaz de línea de comandos
├── core/                       # Módulos centrales
│   ├── __init__.py
│   ├── step_suggester.py       # Sugerencias de pasos
│   ├── report_generator.py     # Generación de reportes
│   ├── element_locator.py      # Localización de elementos
│   ├── variable_manager.py     # Gestión de variables
│   └── project_validator.py    # Validación de proyectos
├── steps/                      # Definiciones de pasos BDD
│   ├── __init__.py
│   ├── navigation_steps.py     # Pasos de navegación
│   ├── interaction_steps.py    # Pasos de interacción
│   ├── assertion_steps.py      # Pasos de verificación
│   ├── variable_steps.py       # Pasos de variables
│   ├── scroll_steps.py         # Pasos de scroll
│   ├── wait_steps.py           # Pasos de espera
│   ├── window_steps.py         # Pasos de ventanas
│   └── advanced_steps.py       # Pasos avanzados
└── templates/                  # Plantillas de proyecto
    ├── __init__.py
    ├── basic/                  # Plantilla básica
    ├── advanced/               # Plantilla avanzada
    └── generators.py           # Generadores de plantillas
```

## Estándares de Código

### Estilo de Código

El proyecto sigue las convenciones de Python con algunas especificaciones:

```python
# Configuración Black
line-length = 100
target-version = ['py38']

# Imports organizados
from typing import Optional, List, Dict, Any
import os
import sys
from pathlib import Path

# Docstrings en formato Google
def example_function(param1: str, param2: Optional[int] = None) -> bool:
    """
    Descripción breve de la función.
    
    Args:
        param1: Descripción del parámetro 1
        param2: Descripción del parámetro 2 (opcional)
    
    Returns:
        Descripción del valor de retorno
        
    Raises:
        ValueError: Cuando param1 está vacío
    """
    if not param1:
        raise ValueError("param1 no puede estar vacío")
    
    return True
```

### Convenciones de Nomenclatura

- **Clases**: PascalCase (`StepSuggester`)
- **Funciones/Métodos**: snake_case (`generate_report`)
- **Variables**: snake_case (`feature_file`)
- **Constantes**: UPPER_SNAKE_CASE (`DEFAULT_TIMEOUT`)
- **Archivos**: snake_case (`step_suggester.py`)

## Desarrollo de Nuevas Funcionalidades

### 1. Agregar Nuevos Pasos BDD

```python
# En steps/custom_steps.py
from behave import given, when, then
from playwright.sync_api import Page

@when('I perform custom action on "{element_name}" with identifier "{identifier}"')
def step_custom_action(context, element_name: str, identifier: str):
    """
    Realiza una acción personalizada en un elemento.
    
    Args:
        context: Contexto de Behave
        element_name: Nombre descriptivo del elemento
        identifier: Identificador del elemento (ej: $.PAGE.element)
    """
    page: Page = context.page
    locator = context.element_locator.get_locator(identifier)
    
    # Implementar lógica personalizada
    element = page.locator(locator)
    element.click()  # Ejemplo
    
    # Logging para Allure
    context.attach_screenshot(f"custom_action_{element_name}")
```

### 2. Crear Nuevos Módulos Core

```python
# En core/new_module.py
from typing import Optional, Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class NewModule:
    """
    Descripción del nuevo módulo.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa el módulo.
        
        Args:
            config: Configuración opcional del módulo
        """
        self.config = config or {}
        self._initialize()
    
    def _initialize(self) -> None:
        """Inicialización interna del módulo."""
        logger.info("Inicializando nuevo módulo")
    
    def main_functionality(self, param: str) -> bool:
        """
        Funcionalidad principal del módulo.
        
        Args:
            param: Parámetro de entrada
            
        Returns:
            True si la operación fue exitosa
        """
        try:
            # Implementar lógica
            return True
        except Exception as e:
            logger.error(f"Error en funcionalidad principal: {e}")
            return False
```

### 3. Extender CLI

```python
# En cli.py
@cli.command()
@click.option('--param', help='Descripción del parámetro')
def new_command(param):
    """Descripción del nuevo comando"""
    
    click.echo(f"🚀 Ejecutando nuevo comando con parámetro: {param}")
    
    try:
        # Implementar lógica del comando
        result = perform_new_operation(param)
        
        if result:
            click.echo("✅ Operación completada exitosamente")
        else:
            click.echo("❌ Error en la operación", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)
```

## Testing

### Estructura de Pruebas

```
tests/
├── unit/                       # Pruebas unitarias
│   ├── test_step_suggester.py
│   ├── test_report_generator.py
│   └── test_element_locator.py
├── integration/                # Pruebas de integración
│   ├── test_cli_commands.py
│   └── test_behave_integration.py
├── e2e/                        # Pruebas end-to-end
│   ├── features/
│   └── test_full_workflow.py
└── fixtures/                   # Datos de prueba
    ├── sample_features/
    └── sample_page_objects/
```

### Escribir Pruebas Unitarias

```python
# tests/unit/test_step_suggester.py
import pytest
from unittest.mock import Mock, patch
from hakalab_framework.core.step_suggester import StepSuggester

class TestStepSuggester:
    
    @pytest.fixture
    def suggester(self):
        """Fixture para crear instancia de StepSuggester."""
        return StepSuggester()
    
    def test_search_steps_with_valid_query(self, suggester):
        """Prueba búsqueda de pasos con query válido."""
        results = suggester.search_steps("click", "en")
        
        assert len(results) > 0
        assert all("click" in step.description.lower() for step in results)
    
    def test_search_steps_with_empty_query(self, suggester):
        """Prueba búsqueda con query vacío."""
        results = suggester.search_steps("", "en")
        
        assert len(results) == 0
    
    @patch('hakalab_framework.core.step_suggester.Path.exists')
    def test_load_steps_file_not_found(self, mock_exists, suggester):
        """Prueba carga de pasos cuando el archivo no existe."""
        mock_exists.return_value = False
        
        with pytest.raises(FileNotFoundError):
            suggester._load_steps_from_file("nonexistent.json")
```

### Ejecutar Pruebas

```bash
# Ejecutar todas las pruebas
pytest

# Ejecutar con cobertura
pytest --cov=hakalab_framework --cov-report=html

# Ejecutar solo pruebas unitarias
pytest tests/unit/

# Ejecutar con verbose
pytest -v

# Ejecutar pruebas específicas
pytest tests/unit/test_step_suggester.py::TestStepSuggester::test_search_steps
```

## Debugging

### Configuración de Debug

```python
# Para debugging con VS Code, crear .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug CLI",
            "type": "python",
            "request": "launch",
            "module": "hakalab_framework.cli",
            "args": ["run", "--feature", "example_login.feature"],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}/examples"
        },
        {
            "name": "Debug Tests",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["tests/unit/test_step_suggester.py", "-v"],
            "console": "integratedTerminal"
        }
    ]
}
```

### Logging

```python
# Configuración de logging
import logging

# En cada módulo
logger = logging.getLogger(__name__)

# Uso en funciones
def example_function():
    logger.debug("Información de debug")
    logger.info("Información general")
    logger.warning("Advertencia")
    logger.error("Error")
    logger.critical("Error crítico")
```

## Contribución

### Flujo de Trabajo Git

```bash
# 1. Crear rama para nueva funcionalidad
git checkout -b feature/nueva-funcionalidad

# 2. Realizar cambios y commits
git add .
git commit -m "feat: agregar nueva funcionalidad"

# 3. Ejecutar pruebas
pytest
black .
flake8

# 4. Push y crear PR
git push origin feature/nueva-funcionalidad
```

### Convenciones de Commits

Seguimos [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` Nueva funcionalidad
- `fix:` Corrección de bug
- `docs:` Cambios en documentación
- `style:` Cambios de formato (no afectan funcionalidad)
- `refactor:` Refactoring de código
- `test:` Agregar o modificar pruebas
- `chore:` Tareas de mantenimiento

### Pull Request Template

```markdown
## Descripción
Breve descripción de los cambios realizados.

## Tipo de cambio
- [ ] Bug fix (cambio que corrige un issue)
- [ ] Nueva funcionalidad (cambio que agrega funcionalidad)
- [ ] Breaking change (cambio que rompe compatibilidad)
- [ ] Documentación

## Checklist
- [ ] Código sigue las convenciones del proyecto
- [ ] Se realizó self-review del código
- [ ] Se agregaron comentarios en código complejo
- [ ] Se agregaron/actualizaron pruebas
- [ ] Todas las pruebas pasan
- [ ] Se actualizó la documentación
```

## Herramientas de Desarrollo

### Configuración de VS Code

```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length", "100"],
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests"],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true
    }
}
```

### Makefile para Automatización

```makefile
# Makefile
.PHONY: install test lint format clean build

install:
	pip install -e ".[dev]"
	python -m playwright install
	pre-commit install

test:
	pytest --cov=hakalab_framework

lint:
	flake8 hakalab_framework tests
	mypy hakalab_framework

format:
	black hakalab_framework tests
	isort hakalab_framework tests

clean:
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	rm -rf build/ dist/ *.egg-info/

build:
	python -m build

publish:
	python -m twine upload dist/*
```

## Troubleshooting

### Problemas Comunes

1. **Error de importación de Playwright**
   ```bash
   # Solución: Instalar navegadores
   python -m playwright install
   ```

2. **Error de permisos en Windows**
   ```bash
   # Solución: Ejecutar como administrador o usar PowerShell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

3. **Problemas con Allure**
   ```bash
   # Solución: Instalar Allure CLI
   npm install -g allure-commandline
   # o usar el reporte simple
   haka-report --simple
   ```

### Debug de Pruebas Behave

```python
# En environment.py para debug
def before_step(context, step):
    print(f"Ejecutando paso: {step.name}")

def after_step(context, step):
    if step.status == "failed":
        print(f"Paso falló: {step.name}")
        # Tomar screenshot
        context.page.screenshot(path=f"failed_{step.name}.png")
```