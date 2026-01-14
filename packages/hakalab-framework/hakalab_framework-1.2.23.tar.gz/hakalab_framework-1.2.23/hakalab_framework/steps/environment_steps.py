#!/usr/bin/env python3
"""
Steps para manejo de variables de entorno desde features
Permite usar variables de entorno directamente en los scenarios
"""
from behave import step
import os
from dotenv import load_dotenv

@step('I load environment variables from file "{env_file}"')
@step('cargo las variables de entorno del archivo "{env_file}"')
def step_load_env_file(context, env_file):
    """Carga variables de entorno desde un archivo específico"""
    resolved_file = context.variable_manager.resolve_variables(env_file)
    
    # Cargar el archivo .env
    if os.path.exists(resolved_file):
        load_dotenv(resolved_file, override=True)
        print(f"✅ Variables de entorno cargadas desde: {resolved_file}")
    else:
        raise FileNotFoundError(f"Archivo de variables de entorno no encontrado: {resolved_file}")

@step('I set environment variable "{var_name}" to "{value}"')
@step('establezco la variable de entorno "{var_name}" con valor "{value}"')
def step_set_env_var(context, var_name, value):
    """Establece una variable de entorno durante la ejecución"""
    resolved_name = context.variable_manager.resolve_variables(var_name)
    resolved_value = context.variable_manager.resolve_variables(value)
    
    # Establecer la variable de entorno
    os.environ[resolved_name] = resolved_value
    print(f"✅ Variable de entorno establecida: {resolved_name}={resolved_value}")

@step('I get environment variable "{var_name}" and store in variable "{variable_name}"')
@step('obtengo variable de entorno "{var_name}" y la guardo en variable "{variable_name}"')
def step_get_env_var(context, var_name, variable_name):
    """Obtiene una variable de entorno y la guarda en una variable del framework"""
    resolved_var_name = context.variable_manager.resolve_variables(var_name)
    
    # Obtener la variable de entorno
    env_value = os.getenv(resolved_var_name)
    
    if env_value is not None:
        context.variable_manager.set_variable(variable_name, env_value)
        print(f"✅ Variable de entorno '{resolved_var_name}' guardada en variable '{variable_name}': {env_value}")
    else:
        raise ValueError(f"Variable de entorno '{resolved_var_name}' no encontrada")

@step('I verify environment variable "{var_name}" exists')
@step('verifico que existe la variable de entorno "{var_name}"')
def step_verify_env_var_exists(context, var_name):
    """Verifica que una variable de entorno existe"""
    resolved_name = context.variable_manager.resolve_variables(var_name)
    
    env_value = os.getenv(resolved_name)
    assert env_value is not None, f"Variable de entorno '{resolved_name}' no existe"
    print(f"✅ Variable de entorno '{resolved_name}' existe: {env_value}")

@step('I verify environment variable "{var_name}" equals "{expected_value}"')
@step('verifico que la variable de entorno "{var_name}" es igual a "{expected_value}"')
def step_verify_env_var_value(context, var_name, expected_value):
    """Verifica que una variable de entorno tiene un valor específico"""
    resolved_name = context.variable_manager.resolve_variables(var_name)
    resolved_expected = context.variable_manager.resolve_variables(expected_value)
    
    env_value = os.getenv(resolved_name)
    assert env_value == resolved_expected, f"Variable de entorno '{resolved_name}' es '{env_value}', esperado '{resolved_expected}'"
    print(f"✅ Variable de entorno '{resolved_name}' verificada: {env_value}")

@step('I navigate to environment URL "{env_var_name}"')
@step('navego a la URL de entorno "{env_var_name}"')
def step_navigate_to_env_url(context, env_var_name):
    """Navega a una URL almacenada en una variable de entorno"""
    resolved_var_name = context.variable_manager.resolve_variables(env_var_name)
    
    # Obtener URL de la variable de entorno
    url = os.getenv(resolved_var_name)
    
    if url is None:
        raise ValueError(f"Variable de entorno '{resolved_var_name}' no encontrada")
    
    # Navegar a la URL
    context.page.goto(url)
    print(f"✅ Navegando a URL desde variable de entorno '{resolved_var_name}': {url}")

@step('I fill field "{field_name}" with environment variable "{env_var_name}" using identifier "{identifier}"')
@step('relleno el campo "{field_name}" con la variable de entorno "{env_var_name}" usando identificador "{identifier}"')
def step_fill_field_with_env_var(context, field_name, env_var_name, identifier):
    """Rellena un campo con el valor de una variable de entorno"""
    resolved_env_name = context.variable_manager.resolve_variables(env_var_name)
    
    # Obtener valor de la variable de entorno
    env_value = os.getenv(resolved_env_name)
    
    if env_value is None:
        raise ValueError(f"Variable de entorno '{resolved_env_name}' no encontrada")
    
    # Rellenar el campo
    locator = context.element_locator.get_locator(identifier)
    context.page.locator(locator).fill(env_value)
    print(f"✅ Campo '{field_name}' rellenado con variable de entorno '{resolved_env_name}': {env_value}")

@step('I use environment credentials to login with username "{username_var}" and password "{password_var}"')
@step('uso credenciales de entorno para login con usuario "{username_var}" y contraseña "{password_var}"')
def step_login_with_env_credentials(context, username_var, password_var):
    """Realiza login usando credenciales almacenadas en variables de entorno"""
    resolved_username_var = context.variable_manager.resolve_variables(username_var)
    resolved_password_var = context.variable_manager.resolve_variables(password_var)
    
    # Obtener credenciales de variables de entorno
    username = os.getenv(resolved_username_var)
    password = os.getenv(resolved_password_var)
    
    if username is None:
        raise ValueError(f"Variable de entorno para username '{resolved_username_var}' no encontrada")
    if password is None:
        raise ValueError(f"Variable de entorno para password '{resolved_password_var}' no encontrada")
    
    # Buscar campos de login (múltiples selectores comunes)
    username_selectors = [
        'input[name="username"]',
        'input[type="email"]',
        'input[id="username"]',
        'input[id="email"]',
        '#user_email',
        '#user_login'
    ]
    
    password_selectors = [
        'input[name="password"]',
        'input[type="password"]',
        'input[id="password"]',
        '#user_password'
    ]
    
    # Rellenar username
    username_filled = False
    for selector in username_selectors:
        username_field = context.page.locator(selector)
        if username_field.count() > 0:
            username_field.first.fill(username)
            username_filled = True
            break
    
    if not username_filled:
        raise AssertionError("Campo de username no encontrado")
    
    # Rellenar password
    password_filled = False
    for selector in password_selectors:
        password_field = context.page.locator(selector)
        if password_field.count() > 0:
            password_field.first.fill(password)
            password_filled = True
            break
    
    if not password_filled:
        raise AssertionError("Campo de password no encontrado")
    
    print(f"✅ Credenciales rellenadas desde variables de entorno: {resolved_username_var}, {resolved_password_var}")

@step('I click login button')
@step('hago click en el botón de login')
def step_click_login_button(context):
    """Hace click en el botón de login (múltiples selectores comunes)"""
    login_selectors = [
        'button[type="submit"]',
        'input[type="submit"]',
        'button:has-text("Log in")',
        'button:has-text("Login")',
        'button:has-text("Sign in")',
        'button:has-text("Iniciar sesión")',
        '#login_button',
        '.login-button',
        '[data-testid="login-button"]'
    ]
    
    login_clicked = False
    for selector in login_selectors:
        login_button = context.page.locator(selector)
        if login_button.count() > 0:
            login_button.first.click()
            login_clicked = True
            break
    
    if not login_clicked:
        raise AssertionError("Botón de login no encontrado")
    
    print("✅ Click en botón de login realizado")

@step('I perform complete login with environment credentials "{username_var}" and "{password_var}"')
@step('realizo login completo con credenciales de entorno "{username_var}" y "{password_var}"')
def step_complete_env_login(context, username_var, password_var):
    """Realiza el proceso completo de login usando variables de entorno"""
    # Usar credenciales de entorno
    step_login_with_env_credentials(context, username_var, password_var)
    
    # Hacer click en login
    step_click_login_button(context)
    
    print("✅ Login completo realizado con credenciales de entorno")

@step('I print all environment variables')
@step('imprimo todas las variables de entorno')
def step_print_all_env_vars(context):
    """Imprime todas las variables de entorno (útil para debugging)"""
    print("\n🔍 Variables de entorno disponibles:")
    for key, value in sorted(os.environ.items()):
        # Ocultar valores sensibles
        if any(sensitive in key.lower() for sensitive in ['password', 'secret', 'key', 'token']):
            print(f"   {key}=***HIDDEN***")
        else:
            print(f"   {key}={value}")

@step('I print environment variables matching pattern "{pattern}"')
@step('imprimo las variables de entorno que coinciden con el patrón "{pattern}"')
def step_print_env_vars_pattern(context, pattern):
    """Imprime variables de entorno que coinciden con un patrón"""
    resolved_pattern = context.variable_manager.resolve_variables(pattern)
    
    print(f"\n🔍 Variables de entorno que contienen '{resolved_pattern}':")
    found_vars = []
    
    for key, value in sorted(os.environ.items()):
        if resolved_pattern.lower() in key.lower():
            # Ocultar valores sensibles
            if any(sensitive in key.lower() for sensitive in ['password', 'secret', 'key', 'token']):
                print(f"   {key}=***HIDDEN***")
            else:
                print(f"   {key}={value}")
            found_vars.append(key)
    
    if not found_vars:
        print(f"   No se encontraron variables que contengan '{resolved_pattern}'")
    else:
        print(f"   Total encontradas: {len(found_vars)}")

@step('I backup environment variable "{var_name}" as "{backup_name}"')
@step('hago backup de la variable de entorno "{var_name}" como "{backup_name}"')
def step_backup_env_var(context, var_name, backup_name):
    """Hace backup de una variable de entorno"""
    resolved_var_name = context.variable_manager.resolve_variables(var_name)
    resolved_backup_name = context.variable_manager.resolve_variables(backup_name)
    
    # Obtener valor actual
    current_value = os.getenv(resolved_var_name)
    
    if current_value is not None:
        # Guardar en variable del framework
        context.variable_manager.set_variable(resolved_backup_name, current_value)
        print(f"✅ Backup realizado: {resolved_var_name} → {resolved_backup_name}")
    else:
        print(f"⚠️ Variable de entorno '{resolved_var_name}' no existe, no se puede hacer backup")

@step('I restore environment variable "{var_name}" from backup "{backup_name}"')
@step('restauro la variable de entorno "{var_name}" desde el backup "{backup_name}"')
def step_restore_env_var(context, var_name, backup_name):
    """Restaura una variable de entorno desde un backup"""
    resolved_var_name = context.variable_manager.resolve_variables(var_name)
    resolved_backup_name = context.variable_manager.resolve_variables(backup_name)
    
    # Obtener valor del backup
    backup_value = context.variable_manager.get_variable(resolved_backup_name)
    
    if backup_value is not None:
        # Restaurar la variable de entorno
        os.environ[resolved_var_name] = backup_value
        print(f"✅ Variable restaurada: {resolved_var_name} = {backup_value}")
    else:
        raise ValueError(f"Backup '{resolved_backup_name}' no encontrado")