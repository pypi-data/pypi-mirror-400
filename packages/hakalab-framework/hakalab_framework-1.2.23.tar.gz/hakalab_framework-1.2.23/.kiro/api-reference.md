# Referencia de API - Haka Framework

## Módulos Core

### StepSuggester

Proporciona sugerencias inteligentes de pasos BDD basadas en patrones y categorías.

```python
from hakalab_framework.core.step_suggester import StepSuggester

suggester = StepSuggester()
```

#### Métodos

##### `search_steps(query: str, language: str = "mixed") -> List[StepInfo]`

Busca pasos que coincidan con la consulta especificada.

**Parámetros:**
- `query`: Palabra clave o frase a buscar
- `language`: Idioma de los pasos ("en", "es", "mixed")

**Retorna:** Lista de objetos `StepInfo` que coinciden con la búsqueda

**Ejemplo:**
```python
results = suggester.search_steps("click", "en")
for step in results:
    print(f"{step.description}: {step.example}")
```

##### `suggest_steps(partial_text: str, language: str = "mixed") -> List[StepInfo]`

Sugiere pasos basados en texto parcial.

**Parámetros:**
- `partial_text`: Texto parcial para generar sugerencias
- `language`: Idioma de los pasos

**Retorna:** Lista de sugerencias de pasos

##### `get_steps_by_category(category: str, language: str = "mixed") -> List[StepInfo]`

Obtiene todos los pasos de una categoría específica.

**Parámetros:**
- `category`: Nombre de la categoría
- `language`: Idioma de los pasos

**Retorna:** Lista de pasos en la categoría especificada

##### `get_all_categories() -> List[str]`

Obtiene todas las categorías disponibles.

**Retorna:** Lista de nombres de categorías

### ReportGenerator

Genera reportes de pruebas en múltiples formatos.

```python
from hakalab_framework.core.report_generator import ReportGenerator

generator = ReportGenerator()
```

#### Métodos

##### `generate_allure_report(single_file: bool = True, open_browser: bool = True) -> bool`

Genera un reporte de Allure.

**Parámetros:**
- `single_file`: Si generar un archivo HTML único
- `open_browser`: Si abrir automáticamente el navegador

**Retorna:** `True` si el reporte se generó exitosamente

**Ejemplo:**
```python
success = generator.generate_allure_report(
    single_file=True,
    open_browser=False
)
```

##### `generate_simple_html_report() -> bool`

Genera un reporte HTML simple como alternativa a Allure.

**Retorna:** `True` si el reporte se generó exitosamente

##### `serve_allure_report(port: int = 8080) -> None`

Sirve el reporte de Allure usando un servidor integrado.

**Parámetros:**
- `port`: Puerto para el servidor

##### `clean_previous_reports() -> None`

Limpia reportes anteriores.

##### `clean_previous_results() -> None`

Limpia resultados de ejecuciones anteriores.

### ElementLocator

Localiza elementos web usando diferentes estrategias de selección.

```python
from hakalab_framework.core.element_locator import ElementLocator

locator = ElementLocator(json_poms_path="json_poms")
```

#### Métodos

##### `get_locator(identifier: str) -> str`

Obtiene el selector de un elemento basado en su identificador.

**Parámetros:**
- `identifier`: Identificador del elemento (ej: "$.LOGIN.username_field")

**Retorna:** Selector CSS, XPath o otro tipo de selector

**Ejemplo:**
```python
selector = locator.get_locator("$.LOGIN.username_field")
# Retorna: "#username"
```

##### `load_page_object(page_name: str) -> Dict[str, Any]`

Carga un Page Object desde archivo JSON.

**Parámetros:**
- `page_name`: Nombre del archivo de Page Object (sin extensión)

**Retorna:** Diccionario con la definición del Page Object

##### `validate_identifier(identifier: str) -> bool`

Valida si un identificador tiene el formato correcto.

**Parámetros:**
- `identifier`: Identificador a validar

**Retorna:** `True` si el identificador es válido

### VariableManager

Gestiona variables dinámicas durante la ejecución de pruebas.

```python
from hakalab_framework.core.variable_manager import VariableManager

var_manager = VariableManager()
```

#### Métodos

##### `set_variable(name: str, value: str) -> None`

Establece el valor de una variable.

**Parámetros:**
- `name`: Nombre de la variable
- `value`: Valor a asignar

**Ejemplo:**
```python
var_manager.set_variable("username", "test@example.com")
```

##### `get_variable(name: str) -> Optional[str]`

Obtiene el valor de una variable.

**Parámetros:**
- `name`: Nombre de la variable

**Retorna:** Valor de la variable o `None` si no existe

##### `interpolate_string(text: str) -> str`

Interpola variables en una cadena de texto.

**Parámetros:**
- `text`: Texto con variables a interpolar (ej: "Hello ${username}")

**Retorna:** Texto con variables reemplazadas

**Ejemplo:**
```python
var_manager.set_variable("name", "John")
result = var_manager.interpolate_string("Hello ${name}")
# result = "Hello John"
```

##### `generate_random_string(length: int) -> str`

Genera una cadena aleatoria de la longitud especificada.

**Parámetros:**
- `length`: Longitud de la cadena

**Retorna:** Cadena aleatoria

##### `generate_uuid() -> str`

Genera un UUID único.

**Retorna:** UUID como string

##### `get_current_timestamp() -> str`

Obtiene el timestamp actual.

**Retorna:** Timestamp como string

## Clases de Datos

### StepInfo

Representa información sobre un paso BDD.

```python
@dataclass
class StepInfo:
    pattern: str          # Patrón regex del paso
    description: str      # Descripción legible del paso
    example: str         # Ejemplo de uso
    category: str        # Categoría del paso
    language: str        # Idioma del paso
    parameters: List[str] # Lista de parámetros
```

### PageObject

Representa un Page Object cargado desde JSON.

```python
@dataclass
class PageObject:
    name: str                    # Nombre del page object
    elements: Dict[str, str]     # Diccionario elemento -> selector
    metadata: Dict[str, Any]     # Metadatos adicionales
```

## Utilidades

### Template Generators

Funciones para generar plantillas de proyecto.

```python
from hakalab_framework.templates import create_project_structure

create_project_structure(
    project_path=Path("mi-proyecto"),
    template="basic",
    language="mixed"
)
```

#### `create_project_structure(project_path: Path, template: str, language: str) -> None`

Crea la estructura completa de un proyecto.

**Parámetros:**
- `project_path`: Ruta donde crear el proyecto
- `template`: Tipo de plantilla ("basic", "advanced")
- `language`: Idioma por defecto ("en", "es", "mixed")

#### `generate_feature_file(feature_name: str, scenarios: List[Dict], language: str) -> str`

Genera el contenido de un archivo .feature.

**Parámetros:**
- `feature_name`: Nombre del feature
- `scenarios`: Lista de escenarios
- `language`: Idioma del feature

**Retorna:** Contenido del archivo .feature

#### `generate_page_object(page_name: str, elements: Dict[str, str]) -> str`

Genera el contenido de un Page Object JSON.

**Parámetros:**
- `page_name`: Nombre de la página
- `elements`: Diccionario de elementos

**Retorna:** Contenido JSON del Page Object

## Hooks de Behave

### Environment Hooks

Hooks disponibles en `environment.py` para personalizar el comportamiento.

```python
def before_all(context):
    """Se ejecuta una vez antes de todas las pruebas."""
    pass

def after_all(context):
    """Se ejecuta una vez después de todas las pruebas."""
    pass

def before_feature(context, feature):
    """Se ejecuta antes de cada feature."""
    pass

def after_feature(context, feature):
    """Se ejecuta después de cada feature."""
    pass

def before_scenario(context, scenario):
    """Se ejecuta antes de cada scenario."""
    pass

def after_scenario(context, scenario):
    """Se ejecuta después de cada scenario."""
    pass

def before_step(context, step):
    """Se ejecuta antes de cada paso."""
    pass

def after_step(context, step):
    """Se ejecuta después de cada paso."""
    if step.status == "failed":
        # Tomar screenshot en caso de fallo
        context.page.screenshot(path=f"failed_{step.name}.png")
```

## Configuración

### Variables de Entorno

Variables disponibles para configurar el comportamiento del framework:

```python
import os

# Configuración del navegador
BROWSER = os.getenv("BROWSER", "chromium")  # chromium, firefox, webkit
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
TIMEOUT = int(os.getenv("TIMEOUT", "30000"))  # milisegundos
SLOW_MO = int(os.getenv("SLOW_MO", "0"))  # milisegundos

# URLs
BASE_URL = os.getenv("BASE_URL", "")
LOGIN_URL = os.getenv("LOGIN_URL", "")

# Credenciales
TEST_EMAIL = os.getenv("TEST_EMAIL", "")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "")

# Reportes
ALLURE_RESULTS_DIR = os.getenv("ALLURE_RESULTS_DIR", "allure-results")
ALLURE_REPORT_DIR = os.getenv("ALLURE_REPORT_DIR", "allure-report")

# Screenshots
SCREENSHOT_ON_FAILURE = os.getenv("SCREENSHOT_ON_FAILURE", "true").lower() == "true"
SCREENSHOT_DIR = os.getenv("SCREENSHOT_DIR", "screenshots")
```

### Configuración de Behave

Configuración disponible en `behave.ini`:

```ini
[behave]
# Rutas de features
paths = features

# Formato de salida
format = allure_behave.formatter:AllureFormatter
outdir = allure-results

# Opciones de visualización
show_timings = true
show_skipped = false
logging_level = INFO

# Configuración de tags
default_tags = -@skip

# Configuración de pasos
step_registry = true
```

## Excepciones

### Excepciones Personalizadas

```python
class HakaFrameworkError(Exception):
    """Excepción base del framework."""
    pass

class ElementNotFoundError(HakaFrameworkError):
    """Se lanza cuando no se encuentra un elemento."""
    pass

class PageObjectNotFoundError(HakaFrameworkError):
    """Se lanza cuando no se encuentra un Page Object."""
    pass

class InvalidIdentifierError(HakaFrameworkError):
    """Se lanza cuando un identificador no es válido."""
    pass

class VariableNotFoundError(HakaFrameworkError):
    """Se lanza cuando no se encuentra una variable."""
    pass

class ReportGenerationError(HakaFrameworkError):
    """Se lanza cuando falla la generación de reportes."""
    pass
```

## Extensiones

### Crear Pasos Personalizados

```python
from behave import given, when, then
from playwright.sync_api import Page

@when('I perform custom action "{action}" on element "{element_name}" with identifier "{identifier}"')
def step_custom_action(context, action: str, element_name: str, identifier: str):
    """
    Realiza una acción personalizada en un elemento.
    
    Args:
        context: Contexto de Behave
        action: Acción a realizar
        element_name: Nombre descriptivo del elemento
        identifier: Identificador del elemento
    """
    page: Page = context.page
    locator = context.element_locator.get_locator(identifier)
    element = page.locator(locator)
    
    if action == "highlight":
        element.highlight()
    elif action == "scroll_into_view":
        element.scroll_into_view_if_needed()
    else:
        raise ValueError(f"Acción no soportada: {action}")
```

### Crear Formatters Personalizados

```python
from behave.formatter.base import Formatter

class CustomFormatter(Formatter):
    """Formatter personalizado para reportes."""
    
    def __init__(self, stream_opener, config):
        super().__init__(stream_opener, config)
        self.stream = stream_opener(name="custom_report.txt")
    
    def feature(self, feature):
        self.stream.write(f"Feature: {feature.name}\n")
    
    def scenario(self, scenario):
        self.stream.write(f"  Scenario: {scenario.name}\n")
    
    def step(self, step):
        status = "✓" if step.status == "passed" else "✗"
        self.stream.write(f"    {status} {step.name}\n")
```

## Integración con CI/CD

### GitHub Actions

```yaml
name: Haka Framework Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install hakalab-framework
        python -m playwright install
    
    - name: Run tests
      run: |
        haka-run --tags @smoke
    
    - name: Generate report
      run: |
        haka-report --simple
    
    - name: Upload report
      uses: actions/upload-artifact@v2
      with:
        name: test-report
        path: allure-report/
```

### Jenkins Pipeline

```groovy
pipeline {
    agent any
    
    stages {
        stage('Setup') {
            steps {
                sh 'pip install hakalab-framework'
                sh 'python -m playwright install'
            }
        }
        
        stage('Test') {
            steps {
                sh 'haka-run --parallel'
            }
        }
        
        stage('Report') {
            steps {
                sh 'haka-report'
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'allure-report',
                    reportFiles: 'index.html',
                    reportName: 'Test Report'
                ])
            }
        }
    }
}
```