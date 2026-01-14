# Guía de Resolución de Problemas - Haka Framework

## Problemas de Instalación

### Error: "No module named 'playwright'"

**Síntomas:**
```
ImportError: No module named 'playwright'
```

**Causas:**
- Playwright no está instalado
- Entorno virtual no activado
- Instalación incompleta

**Soluciones:**
```bash
# Instalar Playwright
pip install playwright

# Instalar navegadores
python -m playwright install

# Verificar instalación
python -c "import playwright; print('Playwright instalado correctamente')"
```

### Error: "Executable doesn't exist at ..."

**Síntomas:**
```
playwright._impl._api_types.Error: Executable doesn't exist at /path/to/browser
```

**Causas:**
- Navegadores de Playwright no instalados
- Instalación corrupta de navegadores

**Soluciones:**
```bash
# Reinstalar navegadores
python -m playwright install

# Instalar navegador específico
python -m playwright install chromium

# Verificar navegadores instalados
python -m playwright install --help
```

### Error: "Permission denied" en Windows

**Síntomas:**
```
PermissionError: [WinError 5] Access is denied
```

**Causas:**
- Permisos insuficientes
- Antivirus bloqueando la instalación
- Política de ejecución de PowerShell

**Soluciones:**
```powershell
# Ejecutar como administrador
# Cambiar política de ejecución
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Desactivar temporalmente el antivirus
# Instalar en directorio con permisos
pip install --user hakalab-framework
```

## Problemas de Configuración

### Error: "behave.ini not found"

**Síntomas:**
```
ConfigError: No configuration file found
```

**Causas:**
- Archivo behave.ini no existe
- Ejecutando desde directorio incorrecto
- Configuración malformada

**Soluciones:**
```bash
# Verificar ubicación actual
pwd

# Crear behave.ini básico
cat > behave.ini << EOF
[behave]
paths = features
format = allure_behave.formatter:AllureFormatter
outdir = allure-results
show_timings = true
logging_level = INFO
EOF

# Validar configuración
haka-validate
```

### Error: "Environment file not found"

**Síntomas:**
```
FileNotFoundError: .env file not found
```

**Causas:**
- Archivo .env no existe
- Variables de entorno no configuradas

**Soluciones:**
```bash
# Crear archivo .env básico
cat > .env << EOF
BROWSER=chromium
HEADLESS=false
TIMEOUT=30000
BASE_URL=https://example.com
TEST_EMAIL=test@example.com
TEST_PASSWORD=password123
EOF

# Verificar variables
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('BROWSER'))"
```

### Error: "JSON Page Object malformed"

**Síntomas:**
```
JSONDecodeError: Expecting property name enclosed in double quotes
```

**Causas:**
- Sintaxis JSON inválida
- Comillas simples en lugar de dobles
- Comas finales

**Soluciones:**
```bash
# Validar JSON
python -m json.tool json_poms/LOGIN.json

# Ejemplo de JSON válido
cat > json_poms/LOGIN.json << EOF
{
  "username_field": "#username",
  "password_field": "#password",
  "login_button": "//button[@type='submit']"
}
EOF
```

## Problemas de Ejecución

### Error: "Element not found"

**Síntomas:**
```
TimeoutError: Timeout 30000ms exceeded.
waiting for selector "#username"
```

**Causas:**
- Selector incorrecto
- Elemento no visible
- Página no cargada completamente
- Timeout insuficiente

**Soluciones:**
```gherkin
# Agregar esperas explícitas
When I wait for the element "username" to be visible with identifier "$.LOGIN.username_field"

# Aumentar timeout en .env
TIMEOUT=60000

# Verificar selector en navegador
# F12 -> Console -> document.querySelector("#username")

# Usar selectores más específicos
"username_field": "input[name='username'][type='text']"
```

### Error: "Page not loaded"

**Síntomas:**
```
Error: Page didn't load within timeout
```

**Causas:**
- URL incorrecta
- Problemas de red
- Página requiere autenticación
- JavaScript no cargado

**Soluciones:**
```gherkin
# Verificar URL
Given I go to the url "${BASE_URL}/login"

# Esperar a que la página cargue
When I wait for network to be idle

# Verificar título de página
Then the page title should contain "Login"

# Aumentar timeout de navegación
# En environment.py:
context.page.set_default_timeout(60000)
```

### Error: "Variable not found"

**Síntomas:**
```
VariableNotFoundError: Variable 'username' not found
```

**Causas:**
- Variable no definida
- Nombre de variable incorrecto
- Scope de variable limitado

**Soluciones:**
```gherkin
# Definir variable antes de usar
Given I set the variable "username" to "test@example.com"
When I fill the field "username" with "${username}" with identifier "$.LOGIN.username_field"

# Verificar variables disponibles
Given I print all variables

# Usar variables de entorno
When I fill the field "username" with "${TEST_EMAIL}" with identifier "$.LOGIN.username_field"
```

## Problemas de Reportes

### Error: "Allure command not found"

**Síntomas:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'allure'
```

**Causas:**
- Allure CLI no instalado
- Allure no en PATH
- Versión incompatible

**Soluciones:**
```bash
# Instalar Allure con npm
npm install -g allure-commandline

# Instalar con Homebrew (macOS)
brew install allure

# Instalar con Scoop (Windows)
scoop install allure

# Verificar instalación
allure --version

# Usar reporte simple como alternativa
haka-report --simple
```

### Error: "No test results found"

**Síntomas:**
```
Warning: No test results found in allure-results
```

**Causas:**
- No se ejecutaron pruebas
- Directorio de resultados incorrecto
- Formatter de Allure no configurado

**Soluciones:**
```bash
# Verificar directorio de resultados
ls -la allure-results/

# Ejecutar pruebas primero
haka-run --feature example_login.feature

# Verificar configuración en behave.ini
[behave]
format = allure_behave.formatter:AllureFormatter
outdir = allure-results

# Limpiar resultados anteriores
haka-report --clean
```

### Error: "Report generation failed"

**Síntomas:**
```
ReportGenerationError: Failed to generate Allure report
```

**Causas:**
- Permisos de escritura
- Espacio en disco insuficiente
- Archivos de resultados corruptos

**Soluciones:**
```bash
# Verificar permisos
chmod 755 allure-report/

# Verificar espacio en disco
df -h

# Limpiar y regenerar
haka-report --clean
haka-run --feature example_login.feature
haka-report

# Usar reporte simple
haka-report --simple
```

## Problemas de Navegador

### Error: "Browser launch failed"

**Síntomas:**
```
Error: Browser launch failed: Failed to launch browser
```

**Causas:**
- Navegador no instalado
- Dependencias del sistema faltantes
- Permisos insuficientes

**Soluciones:**
```bash
# Instalar dependencias del sistema (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libxss1 libasound2

# Reinstalar navegadores
python -m playwright install --with-deps

# Usar modo headless
# En .env:
HEADLESS=true

# Probar navegador específico
haka-run --browser firefox --headless
```

### Error: "Timeout waiting for page"

**Síntomas:**
```
TimeoutError: Timeout 30000ms exceeded waiting for page to load
```

**Causas:**
- Página lenta
- Recursos bloqueados
- JavaScript infinito

**Soluciones:**
```python
# En environment.py aumentar timeouts
def before_all(context):
    context.page.set_default_timeout(60000)
    context.page.set_default_navigation_timeout(60000)

# Deshabilitar imágenes para acelerar
context.page.route("**/*.{png,jpg,jpeg,gif,svg}", lambda route: route.abort())

# Esperar condiciones específicas
When I wait for network to be idle
```

## Problemas de Pasos

### Error: "Step definition not found"

**Síntomas:**
```
NotImplementedError: STEP: When I click on the element "button"
```

**Causas:**
- Paso no implementado
- Importación faltante
- Sintaxis incorrecta

**Soluciones:**
```bash
# Verificar pasos disponibles
haka-steps --search "click"

# Verificar sintaxis correcta
When I click on the element "button name" with identifier "$.PAGE.button"

# Importar pasos en steps/__init__.py
from .navigation_steps import *
from .interaction_steps import *
from .assertion_steps import *
```

### Error: "Invalid identifier format"

**Síntomas:**
```
InvalidIdentifierError: Identifier must start with $.
```

**Causas:**
- Formato de identificador incorrecto
- Page Object no encontrado
- Sintaxis inválida

**Soluciones:**
```gherkin
# Formato correcto
with identifier "$.LOGIN.username_field"

# Verificar Page Object existe
ls json_poms/LOGIN.json

# Verificar contenido del Page Object
cat json_poms/LOGIN.json
```

## Problemas de Variables

### Error: "Environment variable not set"

**Síntomas:**
```
KeyError: 'BASE_URL'
```

**Causas:**
- Variable no definida en .env
- Archivo .env no cargado
- Nombre de variable incorrecto

**Soluciones:**
```bash
# Verificar archivo .env
cat .env

# Cargar variables manualmente
export BASE_URL=https://example.com

# Verificar carga de variables
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.environ.get('BASE_URL'))"
```

### Error: "Variable interpolation failed"

**Síntomas:**
```
ValueError: Invalid variable syntax: ${invalid_var
```

**Causas:**
- Sintaxis de variable incorrecta
- Llaves no cerradas
- Variable no definida

**Soluciones:**
```gherkin
# Sintaxis correcta
"${variable_name}"

# Verificar llaves cerradas
"${BASE_URL}/login"

# Definir variable antes de usar
Given I set the variable "base_url" to "https://example.com"
```

## Problemas de Red

### Error: "Connection refused"

**Síntomas:**
```
ConnectionError: Connection refused
```

**Causas:**
- Servidor no disponible
- URL incorrecta
- Firewall bloqueando

**Soluciones:**
```bash
# Verificar conectividad
ping example.com
curl -I https://example.com

# Verificar URL en .env
echo $BASE_URL

# Usar proxy si es necesario
# En environment.py:
context.browser = playwright.chromium.launch(
    proxy={"server": "http://proxy:8080"}
)
```

### Error: "SSL certificate error"

**Síntomas:**
```
SSLError: certificate verify failed
```

**Causas:**
- Certificado SSL inválido
- Certificado autofirmado
- Configuración SSL estricta

**Soluciones:**
```python
# En environment.py ignorar errores SSL
context.browser = playwright.chromium.launch(
    ignore_https_errors=True
)

# O configurar contexto
context.context = context.browser.new_context(
    ignore_https_errors=True
)
```

## Herramientas de Diagnóstico

### Script de Diagnóstico

```python
#!/usr/bin/env python3
"""
Script de diagnóstico para Haka Framework
"""
import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Verificar versión de Python"""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    if version < (3, 8):
        print("❌ Python 3.8+ requerido")
        return False
    print("✅ Versión de Python OK")
    return True

def check_dependencies():
    """Verificar dependencias instaladas"""
    dependencies = [
        "playwright",
        "behave", 
        "allure-behave",
        "python-dotenv",
        "click"
    ]
    
    for dep in dependencies:
        try:
            __import__(dep.replace("-", "_"))
            print(f"✅ {dep} instalado")
        except ImportError:
            print(f"❌ {dep} no instalado")
            return False
    return True

def check_browsers():
    """Verificar navegadores de Playwright"""
    try:
        result = subprocess.run(
            ["python", "-m", "playwright", "install", "--dry-run"],
            capture_output=True,
            text=True
        )
        if "chromium" in result.stdout:
            print("✅ Navegadores de Playwright disponibles")
            return True
    except Exception:
        pass
    
    print("❌ Navegadores de Playwright no instalados")
    return False

def check_project_structure():
    """Verificar estructura del proyecto"""
    required_files = [
        "features/",
        "json_poms/",
        "behave.ini",
        ".env"
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path} encontrado")
        else:
            print(f"❌ {file_path} no encontrado")
            return False
    return True

def main():
    """Función principal de diagnóstico"""
    print("🔍 Diagnóstico de Haka Framework")
    print("=" * 40)
    
    checks = [
        ("Versión de Python", check_python_version),
        ("Dependencias", check_dependencies),
        ("Navegadores", check_browsers),
        ("Estructura del proyecto", check_project_structure)
    ]
    
    all_passed = True
    for name, check_func in checks:
        print(f"\n{name}:")
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 Todos los checks pasaron!")
    else:
        print("🚨 Se encontraron problemas")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### Comandos de Debug

```bash
# Ejecutar con debug verbose
haka-run --feature login.feature -v

# Verificar configuración
haka-validate

# Listar pasos disponibles
haka-steps

# Generar logs detallados
export BEHAVE_DEBUG_ON_ERROR=yes
haka-run --feature problematic.feature

# Verificar variables de entorno
env | grep -E "(BROWSER|HEADLESS|TIMEOUT|BASE_URL)"

# Probar conectividad
curl -I $BASE_URL

# Verificar permisos
ls -la features/ json_poms/
```

### Logs y Monitoreo

```python
# Configurar logging detallado en environment.py
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

def before_step(context, step):
    logging.info(f"Ejecutando paso: {step.name}")

def after_step(context, step):
    if step.status == "failed":
        logging.error(f"Paso falló: {step.name}")
        # Tomar screenshot
        screenshot_path = f"failed_{step.name.replace(' ', '_')}.png"
        context.page.screenshot(path=screenshot_path)
        logging.info(f"Screenshot guardado: {screenshot_path}")
```

## Contacto y Soporte

Si los problemas persisten después de seguir esta guía:

1. **Verificar Issues**: Buscar en el repositorio de GitHub
2. **Crear Issue**: Incluir logs completos y pasos para reproducir
3. **Documentación**: Revisar la documentación completa
4. **Comunidad**: Participar en discusiones del proyecto

**Información a incluir en reportes de bugs:**
- Versión de Haka Framework
- Versión de Python
- Sistema operativo
- Logs completos
- Pasos para reproducir
- Configuración relevante (.env, behave.ini)