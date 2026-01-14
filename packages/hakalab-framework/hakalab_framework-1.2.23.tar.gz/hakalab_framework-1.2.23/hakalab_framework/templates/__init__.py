"""
Plantillas para crear proyectos
"""
import os
import shutil
from pathlib import Path
from typing import Dict, Any
import json

def create_project_structure(project_path: Path, template: str = "basic", language: str = "mixed"):
    """
    Crea la estructura de un proyecto nuevo
    
    Args:
        project_path: Ruta donde crear el proyecto
        template: Tipo de plantilla (basic, advanced)
        language: Idioma por defecto (en, es, mixed)
    """
    
    # Crear directorio principal
    project_path.mkdir(parents=True, exist_ok=True)
    
    # Crear estructura de directorios
    directories = [
        "features",
        "features/steps",
        "json_poms",
        "test_files",
        "html-reports",
        "screenshots",
        "logs"
    ]
    
    for directory in directories:
        (project_path / directory).mkdir(parents=True, exist_ok=True)
    
    # Crear archivos de configuración
    _create_config_files(project_path, language)
    
    # Crear archivos de ejemplo
    _create_example_files(project_path, template, language)
    
    # Crear archivos de steps (copiar desde el framework)
    _create_steps_files(project_path)
    
    # Crear archivos adicionales
    _create_additional_files(project_path)

def _create_config_files(project_path: Path, language: str):
    """Crea archivos de configuración"""
    
    # requirements.txt
    requirements_content = """playwright>=1.40.0
behave>=1.2.6
behave-parallel>=1.2.6
python-dotenv>=1.0.0
jsonschema>=4.20.0
hakalab-framework>=1.1.2
"""
    
    (project_path / "requirements.txt").write_text(requirements_content)
    
    # .env COMPLETO con todas las opciones
    env_content = """# ========================================
# CONFIGURACIÓN DEL FRAMEWORK HAKALAB
# ========================================

# Configuración de navegador
BROWSER=chromium                    # chromium, firefox, webkit
HEADLESS=false                      # true/false
TIMEOUT=30000                       # Timeout en milisegundos
VIEWPORT_WIDTH=1920                 # Ancho de viewport
VIEWPORT_HEIGHT=1080                # Alto de viewport
SLOW_MO=0                          # Ralentizar acciones (ms)

# URLs y rutas
BASE_URL=https://example.com        # URL base de la aplicación
JSON_POMS_PATH=json_poms           # Ruta a Page Object Models
API_BASE_URL=                      # URL base de API (opcional)

# Reportes y archivos
HTML_REPORTS_DIR=html-reports      # Directorio de reportes HTML
SCREENSHOTS_DIR=screenshots        # Directorio de screenshots
DOWNLOADS_DIR=downloads            # Directorio de descargas

# Configuración de logging
LOG_LEVEL=INFO                     # DEBUG, INFO, WARNING, ERROR
LOG_FILE=                          # Archivo de log (opcional)

# Configuración de red
IGNORE_HTTPS_ERRORS=false          # Ignorar errores HTTPS
USER_AGENT=                        # User Agent personalizado (opcional)

# Configuración de pruebas
AUTO_SCREENSHOT_ON_FAILURE=true    # Screenshot automático en fallos
AUTO_WAIT_FOR_LOAD=true           # Esperar carga automática
RETRY_FAILED_STEPS=0              # Reintentos en pasos fallidos

# ========================================
# DATOS DE PRUEBA
# ========================================
TEST_EMAIL=test@example.com
TEST_PASSWORD=password123
TEST_USER_NAME=Test User

# ========================================
# VARIABLES ESPECÍFICAS DE TU PROYECTO
# ========================================
# Agrega aquí las variables específicas de tu aplicación
# ADMIN_EMAIL=admin@tuapp.com
# ADMIN_PASSWORD=adminpass
# SPECIAL_CONFIG=valor
"""
    
    (project_path / ".env").write_text(env_content)
    
    # behave.ini
    behave_content = """[behave]
paths = features
format = pretty
show_timings = true
show_skipped = false
logging_level = INFO
"""
    
    (project_path / "behave.ini").write_text(behave_content)
    
    # .gitignore
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Framework specific
html-reports/
screenshots/
downloads/
*.png
*.jpg
*.jpeg
*.gif
*.pdf
logs/
*.log

# Environment
.env
.venv
env/
venv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""
    
    (project_path / ".gitignore").write_text(gitignore_content)

def _create_example_files(project_path: Path, template: str, language: str):
    """Crea archivos de ejemplo"""
    
    # Page Object Models de ejemplo
    login_pom = {
        "username_field": "#username",
        "password_field": "#password",
        "login_button": "//button[@type='submit']",
        "error_message": ".error-message",
        "forgot_password_link": "a[href*='forgot-password']",
        "remember_me_checkbox": "#remember-me",
        "signup_link": "//a[contains(text(), 'Sign up')]",
        "loading_spinner": ".spinner",
        "welcome_message": ".welcome-text"
    }
    
    (project_path / "json_poms" / "LOGIN.json").write_text(
        json.dumps(login_pom, indent=2, ensure_ascii=False)
    )
    
    # Feature de ejemplo
    if language == "es":
        feature_content = _get_spanish_feature()
    elif language == "en":
        feature_content = _get_english_feature()
    else:  # mixed
        feature_content = _get_mixed_feature()
    
    (project_path / "features" / "example_login.feature").write_text(feature_content)
    
    # environment.py SÚPER SIMPLE con sistema de screenshots independiente
    environment_content = """# Environment.py súper simple para proyectos existentes
from hakalab_framework import (
    setup_framework_context,
    setup_scenario_context,
    cleanup_scenario_context,
    cleanup_framework_context
)

def before_all(context):
    \"\"\"Configuración inicial - El framework hace todo el trabajo\"\"\"
    setup_framework_context(context)
    
    # 🎯 Aquí puedes agregar configuraciones específicas de tu proyecto
    # context.mi_configuracion_especial = "valor"

def before_scenario(context, scenario):
    \"\"\"Configuración por escenario - El framework maneja todo\"\"\"
    setup_scenario_context(context, scenario)
    
    # 🎯 Aquí puedes agregar lógica específica por escenario
    # if 'special_tag' in scenario.tags:
    #     context.page.goto("https://mi-url-especial.com")

def after_scenario(context, scenario):
    \"\"\"Limpieza por escenario - El framework maneja todo\"\"\"
    cleanup_scenario_context(context, scenario)
    
    # 🎯 Aquí puedes agregar limpieza específica
    # if hasattr(context, 'mi_recurso'):
    #     context.mi_recurso.cleanup()

def after_all(context):
    \"\"\"Limpieza final - El framework maneja todo\"\"\"
    cleanup_framework_context(context)
    
    # 🎯 Aquí puedes agregar limpieza final específica
    # cleanup_mi_configuracion_especial()
"""
    
    (project_path / "features" / "environment.py").write_text(environment_content)

def _create_steps_files(project_path: Path):
    """Crea archivo de steps que importa del framework"""
    
    steps_content = """# Importar todos los pasos del framework
from hakalab_framework.steps import *

# Aquí puedes agregar pasos personalizados para tu proyecto
# Ejemplo:
# 
# from behave import step
# 
# @step('I do something custom')
# def custom_step(context):
#     # Tu lógica personalizada aquí
#     pass
"""
    
    (project_path / "features" / "steps" / "__init__.py").write_text("")
    (project_path / "features" / "steps" / "custom_steps.py").write_text(steps_content)

def _create_additional_files(project_path: Path):
    """Crea archivos adicionales"""
    
    # README.md
    readme_content = f"""# Proyecto de Pruebas Funcionales

Proyecto creado con Playwright Behave Framework.

## 🚀 Instalación

```bash
pip install -r requirements.txt
playwright install
```

## 🎯 Uso Rápido

```bash
# Ejecutar todas las pruebas
behave

# Ejecutar pruebas específicas
behave --tags @smoke
behave features/example_login.feature

# Generar reportes HTML
# Los reportes se generan automáticamente en html-reports/
```

## 📁 Estructura

- `features/` - Archivos .feature con escenarios de prueba
- `features/environment.py` - Configuración súper simple del framework
- `json_poms/` - Page Object Models en formato JSON
- `test_files/` - Archivos para pruebas de upload
- `html-reports/` - Reportes HTML generados
- `.env` - Variables de entorno (toda la configuración aquí)

## ⚙️ Configuración

Todo se configura via variables de entorno en el archivo `.env`:

```properties
# Configuración básica
BROWSER=chromium
HEADLESS=false
BASE_URL=https://tu-aplicacion.com
TIMEOUT=30000

# Datos de prueba
TEST_EMAIL=test@example.com
TEST_PASSWORD=password123

# Configuración avanzada
AUTO_SCREENSHOT_ON_FAILURE=true
VIEWPORT_WIDTH=1920
VIEWPORT_HEIGHT=1080
```

## 🎯 Environment.py Súper Simple

El archivo `features/environment.py` es súper simple - el framework hace todo el trabajo:

```python
from hakalab_framework import (
    setup_framework_context,
    setup_scenario_context,
    cleanup_scenario_context,
    cleanup_framework_context
)

def before_all(context):
    setup_framework_context(context)

def before_scenario(context, scenario):
    setup_scenario_context(context, scenario)

def after_scenario(context, scenario):
    cleanup_scenario_context(context, scenario)

def after_all(context):
    cleanup_framework_context(context)
```

## 📚 Pasos Disponibles

El framework incluye pasos en español e inglés:

```gherkin
# Navegación
Given I go to the url "https://example.com"
Dado que voy a la url "https://example.com"

# Interacciones
When I click on the element "login button" with identifier "$.LOGIN.login_button"
Cuando hago click en el elemento "botón login" con identificador "$.LOGIN.login_button"

# Verificaciones
Then I should see the element "welcome message" with identifier "$.LOGIN.welcome_message"
Entonces debería ver el elemento "mensaje bienvenida" con identificador "$.LOGIN.welcome_message"
```

## 🔧 Personalización

Puedes agregar tu lógica específica en el `environment.py`:

```python
def before_all(context):
    setup_framework_context(context)
    
    # Tu configuración específica
    context.mi_configuracion = "valor"

def before_scenario(context, scenario):
    setup_scenario_context(context, scenario)
    
    # Lógica específica por escenario
    if 'admin' in scenario.tags:
        context.page.goto("https://admin.mi-app.com")
```

## 📊 Reportes

```bash
# Los reportes HTML se generan automáticamente
# Revisa la carpeta html-reports/ después de ejecutar las pruebas

# Para ver screenshots de fallos
ls screenshots/FAILED_*
```

¡El framework maneja automáticamente screenshots en fallos, logging, y toda la configuración de Playwright! 🎉
"""
    
    (project_path / "README.md").write_text(readme_content)
    
    # Archivo de ejemplo para test_files
    (project_path / "test_files" / ".gitkeep").write_text("# Archivos para pruebas de upload")

def _get_english_feature():
    """Feature de ejemplo en inglés"""
    return """@login @smoke
Feature: Login functionality
  As a user
  I want to be able to login to the application
  So that I can access my account

  Background:
    Given I go to the url "https://example.com/login"
    And I wait for the page to load

  @positive
  Scenario: Successful login with valid credentials
    When I fill the field "username" with "testuser@example.com" with identifier "$.LOGIN.username_field"
    And I fill the field "password" with "password123" with identifier "$.LOGIN.password_field"
    And I click on the element "login button" with identifier "$.LOGIN.login_button"
    Then I should see the element "welcome message" with identifier "$.LOGIN.welcome_message"
    And the current url should contain "dashboard"

  @negative
  Scenario: Failed login with invalid credentials
    When I fill the field "username" with "invalid@example.com" with identifier "$.LOGIN.username_field"
    And I fill the field "password" with "wrongpassword" with identifier "$.LOGIN.password_field"
    And I click on the element "login button" with identifier "$.LOGIN.login_button"
    Then I should see the element "error message" with identifier "$.LOGIN.error_message"
    And the element "error message" should contain the text "Invalid credentials" with identifier "$.LOGIN.error_message"
"""

def _get_spanish_feature():
    """Feature de ejemplo en español"""
    return """@login @smoke
Característica: Funcionalidad de login
  Como usuario
  Quiero poder hacer login en la aplicación
  Para poder acceder a mi cuenta

  Antecedentes:
    Dado que voy a la url "https://example.com/login"
    Y espero a que cargue la página

  @positive
  Escenario: Login exitoso con credenciales válidas
    Cuando relleno el campo "usuario" con "testuser@example.com" con identificador "$.LOGIN.username_field"
    Y relleno el campo "contraseña" con "password123" con identificador "$.LOGIN.password_field"
    Y hago click en el elemento "botón login" con identificador "$.LOGIN.login_button"
    Entonces debería ver el elemento "mensaje bienvenida" con identificador "$.LOGIN.welcome_message"
    Y la url actual debería contener "dashboard"

  @negative
  Escenario: Login fallido con credenciales inválidas
    Cuando relleno el campo "usuario" con "invalid@example.com" con identificador "$.LOGIN.username_field"
    Y relleno el campo "contraseña" con "wrongpassword" con identificador "$.LOGIN.password_field"
    Y hago click en el elemento "botón login" con identificador "$.LOGIN.login_button"
    Entonces debería ver el elemento "mensaje error" con identificador "$.LOGIN.error_message"
    Y el elemento "mensaje error" debería contener el texto "Invalid credentials" con identificador "$.LOGIN.error_message"
"""

def _get_mixed_feature():
    """Feature de ejemplo mixto"""
    return """@login @smoke
Feature: Login functionality
  As a user
  I want to be able to login to the application
  So that I can access my account

  Background:
    Given I go to the url "https://example.com/login"
    And I wait for the page to load

  @positive
  Scenario: Successful login with valid credentials
    When I fill the field "username" with "testuser@example.com" with identifier "$.LOGIN.username_field"
    And relleno el campo "password" con "password123" con identificador "$.LOGIN.password_field"
    And I click on the element "login button" with identifier "$.LOGIN.login_button"
    Then debería ver el elemento "welcome message" con identificador "$.LOGIN.welcome_message"
    And the current url should contain "dashboard"

  @mixed_language
  Scenario: Login usando pasos en español e inglés
    Dado que relleno el campo "username" con "usuario@ejemplo.com" con identificador "$.LOGIN.username_field"
    And I fill the field "password" with "contraseña123" with identifier "$.LOGIN.password_field"
    When hago click en el elemento "login button" con identificador "$.LOGIN.login_button"
    Then debería ver el elemento "welcome message" con identificador "$.LOGIN.welcome_message"
"""