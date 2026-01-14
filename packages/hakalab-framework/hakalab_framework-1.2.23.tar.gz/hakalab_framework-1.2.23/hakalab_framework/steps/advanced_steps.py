from behave import step
import json
import os
from datetime import datetime

@step('I execute javascript code "{script}"')
@step('ejecuto el javascript "{script}"')
def step_execute_javascript(context, script):
    """Ejecuta código JavaScript sin guardar resultado"""
    resolved_script = context.variable_manager.resolve_variables(script)
    context.page.evaluate(resolved_script)

@step('I execute javascript "{script}" and store result in variable "{variable_name}"')
@step('ejecuto javascript "{script}" y guardo el resultado en la variable "{variable_name}"')
@step('que ejecuto javascript "{script}" y guardo el resultado en la variable "{variable_name}"')
def step_execute_javascript_and_store(context, script, variable_name):
    """Ejecuta código JavaScript y guarda el resultado"""
    resolved_script = context.variable_manager.resolve_variables(script)
    result = context.page.evaluate(resolved_script)
    context.variable_manager.set_variable(variable_name, result)

@step('I take a screenshot')
@step('I take a screenshot with name "{filename}"')
@step('tomo una captura de pantalla')
@step('tomo una captura de pantalla con nombre "{filename}"')
@step('que tomo una captura de pantalla')
@step('que tomo una captura de pantalla con nombre "{filename}"')
def step_take_screenshot(context, filename=None):
    """Toma una captura de pantalla"""
    try:
        # Obtener directorio de screenshots desde variables de entorno
        screenshot_dir = os.getenv('SCREENSHOTS_DIR', 'screenshots')
        
        # Crear directorio si no existe
        os.makedirs(screenshot_dir, exist_ok=True)
        
        # Generar nombre de archivo si no se proporciona
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
        elif not filename.endswith('.png'):
            filename += '.png'
        
        # Tomar screenshot con configuración de página completa
        screenshot_path = os.path.join(screenshot_dir, filename)
        full_page = os.getenv('SCREENSHOT_FULL_PAGE', 'true').lower() == 'true'
        context.page.screenshot(path=screenshot_path, full_page=full_page, type='png')
        
        if hasattr(context, 'logger'):
            context.logger.info(f"Screenshot guardado: {screenshot_path}")
        
        return screenshot_path
    except Exception as e:
        if hasattr(context, 'logger'):
            context.logger.error(f"Error tomando screenshot: {e}")
        raise

@step('I drag element "{source_element}" to element "{target_element}" with source identifier "{source_id}" and target identifier "{target_id}"')
@step('arrastro el elemento "{source_element}" al elemento "{target_element}" con identificador origen "{source_id}" e identificador destino "{target_id}"')
@step('que arrastro el elemento "{source_element}" al elemento "{target_element}" con identificador origen "{source_id}" e identificador destino "{target_id}"')
def step_drag_and_drop(context, source_element, target_element, source_id, target_id):
    """Arrastra un elemento y lo suelta en otro"""
    source_locator = context.element_locator.get_locator(source_id)
    target_locator = context.element_locator.get_locator(target_id)
    context.page.drag_and_drop(source_locator, target_locator)

@step('I set cookie "{name}" with value "{value}"')
@step('establezco la cookie "{name}" con valor "{value}"')
@step('que establezco la cookie "{name}" con valor "{value}"')
def step_set_cookie(context, name, value):
    """Establece una cookie"""
    resolved_value = context.variable_manager.resolve_variables(value)
    context.page.context.add_cookies([{
        'name': name,
        'value': resolved_value,
        'url': context.page.url
    }])

@step('I get cookie "{name}" and store it in variable "{variable_name}"')
@step('obtengo la cookie "{name}" y la guardo en la variable "{variable_name}"')
@step('que obtengo la cookie "{name}" y la guardo en la variable "{variable_name}"')
def step_get_cookie(context, name, variable_name):
    """Obtiene una cookie y la guarda en una variable"""
    cookies = context.page.context.cookies()
    for cookie in cookies:
        if cookie['name'] == name:
            context.variable_manager.set_variable(variable_name, cookie['value'])
            return
    raise Exception(f"Cookie '{name}' no encontrada")

@step('I delete cookie "{name}"')
@step('elimino la cookie "{name}"')
@step('que elimino la cookie "{name}"')
def step_delete_cookie(context, name):
    """Elimina una cookie específica"""
    context.page.context.clear_cookies(name=name)

@step('I clear all cookies')
@step('limpio todas las cookies')
@step('que limpio todas las cookies')
def step_clear_all_cookies(context):
    """Limpia todas las cookies"""
    context.page.context.clear_cookies()

@step('I set local storage item "{key}" to "{value}"')
@step('establezco el elemento de local storage "{key}" con valor "{value}"')
@step('que establezco el elemento de local storage "{key}" con valor "{value}"')
def step_set_local_storage(context, key, value):
    """Establece un elemento en el local storage"""
    resolved_value = context.variable_manager.resolve_variables(value)
    context.page.evaluate(f"localStorage.setItem('{key}', '{resolved_value}')")

@step('I get local storage item "{key}" and store it in variable "{variable_name}"')
@step('obtengo el elemento de local storage "{key}" y lo guardo en la variable "{variable_name}"')
@step('que obtengo el elemento de local storage "{key}" y lo guardo en la variable "{variable_name}"')
def step_get_local_storage(context, key, variable_name):
    """Obtiene un elemento del local storage"""
    value = context.page.evaluate(f"localStorage.getItem('{key}')")
    context.variable_manager.set_variable(variable_name, value)

@step('I clear local storage')
@step('limpio el local storage')
@step('que limpio el local storage')
def step_clear_local_storage(context):
    """Limpia el local storage"""
    context.page.evaluate("localStorage.clear()")

@step('I set session storage item "{key}" to "{value}"')
@step('establezco el elemento de session storage "{key}" con valor "{value}"')
@step('que establezco el elemento de session storage "{key}" con valor "{value}"')
def step_set_session_storage(context, key, value):
    """Establece un elemento en el session storage"""
    resolved_value = context.variable_manager.resolve_variables(value)
    context.page.evaluate(f"sessionStorage.setItem('{key}', '{resolved_value}')")

@step('I get session storage item "{key}" and store it in variable "{variable_name}"')
@step('obtengo el elemento de session storage "{key}" y lo guardo en la variable "{variable_name}"')
@step('que obtengo el elemento de session storage "{key}" y lo guardo en la variable "{variable_name}"')
def step_get_session_storage(context, key, variable_name):
    """Obtiene un elemento del session storage"""
    value = context.page.evaluate(f"sessionStorage.getItem('{key}')")
    context.variable_manager.set_variable(variable_name, value)

@step('I simulate key combination "{keys}"')
@step('simulo la combinación de teclas "{keys}"')
@step('que simulo la combinación de teclas "{keys}"')
def step_key_combination(context, keys):
    """Simula una combinación de teclas"""
    resolved_keys = context.variable_manager.resolve_variables(keys)
    context.page.keyboard.press(resolved_keys)

@step('I set browser geolocation to latitude {latitude:f} and longitude {longitude:f}')
@step('establezco la geolocalización del navegador a latitud {latitude:f} y longitud {longitude:f}')
@step('que establezco la geolocalización del navegador a latitud {latitude:f} y longitud {longitude:f}')
def step_set_geolocation(context, latitude, longitude):
    """Establece la geolocalización del navegador"""
    context.page.context.set_geolocation({"latitude": latitude, "longitude": longitude})

@step('I emulate device "{device_name}"')
@step('emulo el dispositivo "{device_name}"')
@step('que emulo el dispositivo "{device_name}"')
def step_emulate_device(context, device_name):
    """Emula un dispositivo específico"""
    from playwright.sync_api import devices
    if device_name in devices:
        device = devices[device_name]
        context.page.set_viewport_size(device['viewport'])
        context.page.set_extra_http_headers(device.get('extraHTTPHeaders', {}))
    else:
        raise Exception(f"Dispositivo '{device_name}' no encontrado")