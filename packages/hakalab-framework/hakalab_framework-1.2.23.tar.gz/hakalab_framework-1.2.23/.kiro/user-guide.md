# Guía de Usuario - Haka Framework

## Introducción

El Haka Framework es una herramienta completa para crear y ejecutar pruebas funcionales automatizadas de aplicaciones web. Combina la potencia de Playwright para automatización web con Behave para desarrollo dirigido por comportamiento (BDD).

## Instalación

### Instalación desde PyPI (Recomendado)

```bash
# Instalar el framework
pip install hakalab-framework

# Instalar navegadores de Playwright
python -m playwright install

# Verificar instalación
haka-validate
```

### Instalación desde Código Fuente

```bash
# Clonar repositorio
git clone https://github.com/pipefariashaka/hakalab-framework.git
cd hakalab-framework

# Instalar en modo desarrollo
pip install -e .

# Instalar navegadores
python -m playwright install
```

## Inicio Rápido

### 1. Crear un Nuevo Proyecto

```bash
# Crear proyecto básico
haka-init mi-proyecto-pruebas

# Crear proyecto avanzado
haka-init mi-proyecto-avanzado --template advanced

# Crear proyecto en español
haka-init mi-proyecto-es --language es
```

### 2. Estructura del Proyecto Generado

```
mi-proyecto-pruebas/
├── features/                   # Archivos de pruebas
│   ├── environment.py          # Configuración de Behave
│   ├── example_login.feature   # Ejemplo de login
│   └── steps/                  # Definiciones de pasos personalizados
├── json_poms/                  # Page Object Models
│   ├── LOGIN.json              # Elementos de login
│   └── HOMEPAGE.json           # Elementos de homepage
├── test_files/                 # Archivos para pruebas de upload
├── .env                        # Variables de entorno
├── behave.ini                  # Configuración de Behave
└── requirements.txt            # Dependencias
```

### 3. Ejecutar Pruebas de Ejemplo

```bash
cd mi-proyecto-pruebas

# Ejecutar todas las pruebas
haka-run

# Ejecutar feature específico
haka-run --feature example_login.feature

# Ejecutar con tags
haka-run --tags @smoke
```

### 4. Generar Reportes

```bash
# Generar reporte de Allure
haka-report

# Servir reporte con servidor integrado
haka-report --serve

# Generar reporte simple (sin Allure)
haka-report --simple
```

## Configuración

### Variables de Entorno (.env)

```bash
# Configuración del navegador
BROWSER=chromium              # chromium, firefox, webkit
HEADLESS=false               # true para modo sin interfaz
TIMEOUT=30000                # Timeout en milisegundos
SLOW_MO=0                    # Ralentizar acciones (ms)

# URLs base
BASE_URL=https://example.com
LOGIN_URL=https://example.com/login

# Credenciales de prueba
TEST_EMAIL=test@example.com
TEST_PASSWORD=password123
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin123

# Configuración de reportes
ALLURE_RESULTS_DIR=allure-results
ALLURE_REPORT_DIR=allure-report

# Configuración de screenshots
SCREENSHOT_ON_FAILURE=true
SCREENSHOT_DIR=screenshots
```

### Configuración de Behave (behave.ini)

```ini
[behave]
paths = features
format = allure_behave.formatter:AllureFormatter
outdir = allure-results
show_timings = true
logging_level = INFO
show_skipped = false
```

## Page Object Models en JSON

### Estructura de un Page Object

```json
{
  "page_title": "Login Page",
  "base_url": "https://example.com/login",
  "elements": {
    "username_field": "#username",
    "password_field": "#password",
    "login_button": "//button[@type='submit']",
    "error_message": ".error-message",
    "forgot_password_link": "a[href*='forgot-password']",
    "remember_me_checkbox": "#remember-me",
    "welcome_message": ".welcome-message"
  },
  "metadata": {
    "description": "Elementos de la página de login",
    "author": "Tu Nombre",
    "version": "1.0"
  }
}
```

### Tipos de Selectores Soportados

- **CSS Selector**: `#id`, `.class`, `tag[attribute='value']`
- **XPath**: `//div[@class='example']`, `//button[text()='Click']`
- **ID**: `#element-id`
- **Class**: `.class-name`
- **Name**: `[name='field-name']`
- **Tag**: `button`, `input`, `div`

## Escribir Features

### Sintaxis Básica

```gherkin
@login @smoke
Feature: Funcionalidad de Login
  Como usuario del sistema
  Quiero poder iniciar sesión
  Para acceder a mi cuenta

  Background:
    Given I go to the url "${LOGIN_URL}"

  @positive
  Scenario: Login exitoso con credenciales válidas
    When I fill the field "username" with "${TEST_EMAIL}" with identifier "$.LOGIN.username_field"
    And I fill the field "password" with "${TEST_PASSWORD}" with identifier "$.LOGIN.password_field"
    And I click on the element "login button" with identifier "$.LOGIN.login_button"
    Then I should see the element "welcome message" with identifier "$.LOGIN.welcome_message"
    And the current url should contain "dashboard"

  @negative
  Scenario: Login fallido con credenciales inválidas
    When I fill the field "username" with "invalid@email.com" with identifier "$.LOGIN.username_field"
    And I fill the field "password" with "wrongpassword" with identifier "$.LOGIN.password_field"
    And I click on the element "login button" with identifier "$.LOGIN.login_button"
    Then I should see the element "error message" with identifier "$.LOGIN.error_message"
    And the element "error message" should contain the text "Invalid credentials" with identifier "$.LOGIN.error_message"
```

### Scenario Outlines (Pruebas Parametrizadas)

```gherkin
@data-driven
Scenario Outline: Login con diferentes usuarios
  When I fill the field "username" with "<username>" with identifier "$.LOGIN.username_field"
  And I fill the field "password" with "<password>" with identifier "$.LOGIN.password_field"
  And I click on the element "login button" with identifier "$.LOGIN.login_button"
  Then the current url should contain "<expected_page>"

  Examples:
    | username              | password    | expected_page |
    | admin@example.com     | admin123    | admin         |
    | user@example.com      | user123     | dashboard     |
    | manager@example.com   | manager123  | management    |
```

## Pasos Disponibles

### Navegación

```gherkin
# Inglés
Given I go to the url "https://example.com"
When I go back
When I go forward
When I reload the page
When I wait for {seconds} seconds

# Español
Dado que voy a la url "https://example.com"
Cuando voy hacia atrás
Cuando voy hacia adelante
Cuando recargo la página
Cuando espero {seconds} segundos
```

### Interacciones con Elementos

```gherkin
# Clicks
When I click on the element "button name" with identifier "$.PAGE.button"
When I double click on the element "button name" with identifier "$.PAGE.button"
When I right click on the element "button name" with identifier "$.PAGE.button"

# Formularios
When I fill the field "field name" with "text value" with identifier "$.PAGE.field"
When I clear the field "field name" with identifier "$.PAGE.field"
When I select the option "option text" from dropdown "dropdown name" with identifier "$.PAGE.dropdown"
When I check the checkbox "checkbox name" with identifier "$.PAGE.checkbox"
When I uncheck the checkbox "checkbox name" with identifier "$.PAGE.checkbox"

# Interacciones avanzadas
When I hover over the element "element name" with identifier "$.PAGE.element"
When I drag element "source" to element "target" with source identifier "$.PAGE.source" and target identifier "$.PAGE.target"
```

### Verificaciones (Assertions)

```gherkin
# Visibilidad
Then I should see the element "element name" with identifier "$.PAGE.element"
Then I should not see the element "element name" with identifier "$.PAGE.element"

# Contenido de texto
Then the element "element name" should contain the text "expected text" with identifier "$.PAGE.element"
Then the element "element name" should not contain the text "unexpected text" with identifier "$.PAGE.element"
Then the element "element name" should have exact text "exact text" with identifier "$.PAGE.element"

# Valores de campos
Then the field "field name" should have the value "expected value" with identifier "$.PAGE.field"
Then the field "field name" should be empty with identifier "$.PAGE.field"

# Estados de elementos
Then the element "element name" should be enabled with identifier "$.PAGE.element"
Then the element "element name" should be disabled with identifier "$.PAGE.element"
Then the checkbox "checkbox name" should be checked with identifier "$.PAGE.checkbox"
Then the checkbox "checkbox name" should be unchecked with identifier "$.PAGE.checkbox"

# URL y página
Then the current url should be "https://expected-url.com"
Then the current url should contain "expected-fragment"
Then the page title should be "Expected Title"
Then the page title should contain "Expected Fragment"
```

### Variables Dinámicas

```gherkin
# Definir variables
Given I set the variable "username" to "test@example.com"
Given I set the variable "random_id" to a random string of length 8
Given I set the variable "timestamp" to the current timestamp
Given I set the variable "uuid" to a random UUID

# Extraer datos de elementos
When I get the text from element "element name" and store it in variable "var_name" with identifier "$.PAGE.element"
When I get the value from field "field name" and store it in variable "var_name" with identifier "$.PAGE.field"
When I get the attribute "href" from element "link" and store it in variable "var_name" with identifier "$.PAGE.link"

# Usar variables (con interpolación)
When I fill the field "username" with "${username}" with identifier "$.PAGE.username_field"
Then the element "welcome" should contain the text "Hello ${username}" with identifier "$.PAGE.welcome"

# Operaciones con variables
Given I concatenate "${first_name}" and "${last_name}" and store in variable "full_name"
Given I generate a random email and store it in variable "random_email"
```

### Scroll y Navegación

```gherkin
# Scroll
When I scroll to the element "element name" with identifier "$.PAGE.element"
When I scroll to the top of the page
When I scroll to the bottom of the page
When I scroll down 500 pixels
When I scroll up 300 pixels

# Esperas
When I wait for the element "element name" to be visible with identifier "$.PAGE.element"
When I wait for the element "element name" to be hidden with identifier "$.PAGE.element"
When I wait for the page url to contain "expected-fragment"
When I wait for network to be idle
```

### Ventanas y Pestañas

```gherkin
# Manejo de ventanas
When I open a new tab
When I switch to the new window
When I switch to the main window
When I close the current tab

# Screenshots
When I take a screenshot and save it as "screenshot_name"
When I take a full page screenshot and save it as "full_screenshot"
```

### Elementos Avanzados

```gherkin
# JavaScript
When I execute javascript "document.title = 'New Title'"
When I execute javascript "window.scrollTo(0, 0)"

# Cookies y Storage
When I set cookie "session_id" with value "abc123"
When I delete cookie "session_id"
When I set local storage item "user_preference" to "dark_mode"
When I set session storage item "temp_data" to "value123"

# Archivos
When I upload file "test_files/sample.pdf" to element "file input" with identifier "$.PAGE.file_input"

# Alerts y Dialogs
When I accept the alert
When I dismiss the alert
When I fill the prompt with "response text"
```

## Comandos CLI

### haka-init

Inicializa un nuevo proyecto de pruebas.

```bash
# Sintaxis
haka-init <nombre_proyecto> [opciones]

# Opciones
--template basic|advanced    # Plantilla de proyecto (default: basic)
--language en|es|mixed       # Idioma por defecto (default: mixed)

# Ejemplos
haka-init mi-proyecto
haka-init proyecto-avanzado --template advanced
haka-init proyecto-español --language es
```

### haka-run

Ejecuta las pruebas del proyecto.

```bash
# Sintaxis
haka-run [opciones]

# Opciones
--tags TAG                   # Filtrar por tags (puede repetirse)
--feature FEATURE           # Ejecutar feature específico
--parallel                  # Ejecutar en paralelo
--list-features             # Listar features disponibles
--browser chromium|firefox|webkit  # Navegador a usar
--headless                  # Ejecutar sin interfaz gráfica

# Ejemplos
haka-run                                    # Todas las pruebas
haka-run --feature login.feature           # Feature específico
haka-run --tags @smoke                     # Solo pruebas smoke
haka-run --tags @smoke --tags @regression  # Múltiples tags
haka-run --parallel --browser firefox      # Paralelo con Firefox
haka-run --list-features                   # Listar features
```

### haka-report

Genera reportes de las pruebas ejecutadas.

```bash
# Sintaxis
haka-report [opciones]

# Opciones
--serve                     # Servir reporte con servidor integrado
--port PORT                 # Puerto para servidor (default: 8080)
--simple                    # Generar reporte HTML simple
--clean                     # Limpiar reportes anteriores
--no-browser               # No abrir navegador automáticamente

# Ejemplos
haka-report                 # Generar reporte Allure
haka-report --serve         # Servir con servidor integrado
haka-report --simple        # Reporte simple sin Allure
haka-report --clean         # Limpiar reportes anteriores
```

### haka-steps

Explora y sugiere pasos disponibles.

```bash
# Sintaxis
haka-steps [opciones]

# Opciones
--search KEYWORD            # Buscar pasos por palabra clave
--category CATEGORY         # Filtrar por categoría
--language en|es|mixed      # Idioma (default: mixed)
--suggest TEXT              # Sugerir pasos para texto parcial
--generate-docs             # Generar documentación completa

# Ejemplos
haka-steps                          # Mostrar resumen de categorías
haka-steps --search "click"         # Buscar pasos con "click"
haka-steps --category "Navegación"  # Pasos de navegación
haka-steps --suggest "I want to"    # Sugerencias para texto
haka-steps --generate-docs          # Generar documentación
```

### haka-validate

Valida la configuración del proyecto.

```bash
# Sintaxis
haka-validate

# Verifica:
# - Estructura de directorios
# - Archivos de configuración
# - Dependencias instaladas
# - Configuración de Behave
```

## Mejores Prácticas

### Organización de Features

```
features/
├── authentication/
│   ├── login.feature
│   ├── logout.feature
│   └── password_reset.feature
├── user_management/
│   ├── create_user.feature
│   ├── edit_user.feature
│   └── delete_user.feature
└── reporting/
    ├── generate_report.feature
    └── export_data.feature
```

### Uso de Tags

```gherkin
@smoke @critical @login
Feature: Login functionality

@smoke @positive
Scenario: Successful login

@regression @negative
Scenario: Failed login with invalid credentials

@slow @integration
Scenario: Login with external authentication
```

### Nomenclatura de Variables

```gherkin
# Variables de configuración
${BASE_URL}
${LOGIN_URL}
${API_ENDPOINT}

# Credenciales
${ADMIN_EMAIL}
${ADMIN_PASSWORD}
${TEST_USER_EMAIL}

# Datos dinámicos
${random_username}
${current_timestamp}
${generated_uuid}
```

### Manejo de Datos Sensibles

```bash
# En .env (nunca commitear)
PROD_ADMIN_PASSWORD=super_secret_password
API_KEY=your_api_key_here

# En features usar variables
When I fill the field "password" with "${PROD_ADMIN_PASSWORD}" with identifier "$.LOGIN.password_field"
```

## Troubleshooting

### Problemas Comunes

1. **Error: "No se encuentra el elemento"**
   ```
   Solución: Verificar el selector en json_poms/ y agregar esperas explícitas
   ```

2. **Error: "Timeout esperando elemento"**
   ```
   Solución: Aumentar TIMEOUT en .env o usar pasos de espera específicos
   ```

3. **Error: "Navegador no se abre"**
   ```
   Solución: Ejecutar 'python -m playwright install'
   ```

4. **Error: "Allure no encontrado"**
   ```
   Solución: Usar 'haka-report --simple' o instalar Allure CLI
   ```

### Debug de Pruebas

```bash
# Ejecutar con modo verbose
haka-run --feature login.feature -v

# Ejecutar sin headless para ver el navegador
# En .env: HEADLESS=false

# Tomar screenshots en cada paso
# En .env: SCREENSHOT_ON_FAILURE=true
```

### Logs y Diagnósticos

```bash
# Ver logs detallados
export BEHAVE_DEBUG_ON_ERROR=yes
haka-run --feature problematic.feature

# Validar configuración
haka-validate

# Verificar pasos disponibles
haka-steps --search "problema"
```