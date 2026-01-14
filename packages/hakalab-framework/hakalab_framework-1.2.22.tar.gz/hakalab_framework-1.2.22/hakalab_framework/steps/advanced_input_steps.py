#!/usr/bin/env python3
"""
Steps avanzados para interacción con campos de entrada
Incluye escritura gradual, limpieza avanzada, y manipulación de texto
"""
import time
import random
from behave import step

@step('escribo gradualmente "{text}" en "{selector}" con {delay:d}ms entre caracteres')
@step('que escribo gradualmente "{text}" en "{selector}" con delay de {delay:d}ms')
@step('ingreso letra por letra "{text}" en "{selector}" esperando {delay:d}ms')
def step_type_text_gradually(context, text, selector, delay):
    """Escribe texto gradualmente, carácter por carácter"""
    # Resolver variables en el texto
    if hasattr(context, 'variable_manager'):
        text = context.variable_manager.resolve_variables(text)
    
    # Obtener elemento
    if hasattr(context, 'get_element'):
        element = context.get_element(selector)
    else:
        element = context.page.locator(selector)
    
    # Limpiar campo primero
    element.click()
    element.clear()
    
    # Escribir carácter por carácter
    print(f"⌨️ Escribiendo '{text}' gradualmente en {selector} (delay: {delay}ms)...")
    for char in text:
        element.type(char)
        time.sleep(delay / 1000)  # Convertir ms a segundos
    
    print(f"✅ Texto '{text}' ingresado gradualmente en: {selector}")

@step('escribo naturalmente "{text}" en "{selector}"')
@step('que escribo naturalmente "{text}" en "{selector}"')
def step_type_text_naturally(context, text, selector):
    """Escribe texto simulando escritura humana con delays variables"""
    # Resolver variables en el texto
    if hasattr(context, 'variable_manager'):
        text = context.variable_manager.resolve_variables(text)
    
    # Obtener elemento
    if hasattr(context, 'get_element'):
        element = context.get_element(selector)
    else:
        element = context.page.locator(selector)
    
    # Limpiar campo primero
    element.click()
    element.clear()
    
    # Escribir con delays aleatorios (50-200ms)
    print(f"⌨️ Escribiendo '{text}' naturalmente en {selector}...")
    for char in text:
        element.type(char)
        delay = random.randint(50, 200) / 1000  # 50-200ms
        time.sleep(delay)
    
    print(f"✅ Texto '{text}' ingresado naturalmente en: {selector}")

@step('limpio completamente el campo "{selector}"')
@step('que limpio totalmente "{selector}"')
@step('borro todo el contenido de "{selector}"')
def step_clear_field_completely(context, selector):
    """Limpia completamente un campo de entrada usando múltiples métodos"""
    # Obtener elemento
    if hasattr(context, 'get_element'):
        element = context.get_element(selector)
    else:
        element = context.page.locator(selector)
    
    # Limpiar usando múltiples métodos para asegurar que funcione
    element.click()
    element.clear()
    
    # Método alternativo: seleccionar todo y borrar
    element.press('Control+a')
    element.press('Delete')
    
    # Verificar que está vacío
    current_value = element.input_value()
    if current_value:
        # Si aún tiene contenido, usar método más agresivo
        element.press('Control+a')
        element.press('Backspace')
    
    print(f"✅ Campo completamente limpiado: {selector}")

@step('selecciono todo el texto en "{selector}" y lo borro')
@step('que selecciono y borro todo en "{selector}"')
def step_select_all_and_delete(context, selector):
    """Selecciona todo el texto y lo borra"""
    # Obtener elemento
    if hasattr(context, 'get_element'):
        element = context.get_element(selector)
    else:
        element = context.page.locator(selector)
    
    # Hacer clic para enfocar
    element.click()
    
    # Seleccionar todo y borrar
    element.press('Control+a')
    element.press('Delete')
    
    print(f"✅ Texto seleccionado y borrado en: {selector}")

@step('borro {num_chars:d} caracteres del final en "{selector}"')
@step('que borro {num_chars:d} caracteres de "{selector}"')
def step_delete_characters(context, num_chars, selector):
    """Borra un número específico de caracteres del final"""
    # Obtener elemento
    if hasattr(context, 'get_element'):
        element = context.get_element(selector)
    else:
        element = context.page.locator(selector)
    
    # Hacer clic para enfocar
    element.click()
    
    # Mover cursor al final y borrar caracteres
    element.press('End')
    for _ in range(num_chars):
        element.press('Backspace')
    
    print(f"✅ {num_chars} caracteres borrados del final en: {selector}")

@step('reemplazo el texto en "{selector}" con "{new_text}"')
@step('que cambio el texto de "{selector}" por "{new_text}"')
def step_replace_text(context, selector, new_text):
    """Reemplaza completamente el texto en un campo"""
    # Resolver variables en el nuevo texto
    if hasattr(context, 'variable_manager'):
        new_text = context.variable_manager.resolve_variables(new_text)
    
    # Obtener elemento
    if hasattr(context, 'get_element'):
        element = context.get_element(selector)
    else:
        element = context.page.locator(selector)
    
    # Limpiar y escribir nuevo texto
    element.click()
    element.press('Control+a')
    element.type(new_text)
    
    print(f"✅ Texto reemplazado en {selector} con: '{new_text}'")

@step('agrego "{additional_text}" al final del texto en "{selector}"')
@step('que agrego "{additional_text}" al final de "{selector}"')
def step_append_text(context, additional_text, selector):
    """Agrega texto al final del contenido existente"""
    # Resolver variables
    if hasattr(context, 'variable_manager'):
        additional_text = context.variable_manager.resolve_variables(additional_text)
    
    # Obtener elemento
    if hasattr(context, 'get_element'):
        element = context.get_element(selector)
    else:
        element = context.page.locator(selector)
    
    # Mover cursor al final y agregar texto
    element.click()
    element.press('End')
    element.type(additional_text)
    
    print(f"✅ Texto '{additional_text}' agregado al final de: {selector}")

@step('inserto "{text}" al inicio del campo "{selector}"')
@step('que inserto "{text}" al principio de "{selector}"')
def step_prepend_text(context, text, selector):
    """Inserta texto al inicio del contenido existente"""
    # Resolver variables
    if hasattr(context, 'variable_manager'):
        text = context.variable_manager.resolve_variables(text)
    
    # Obtener elemento
    if hasattr(context, 'get_element'):
        element = context.get_element(selector)
    else:
        element = context.page.locator(selector)
    
    # Mover cursor al inicio y agregar texto
    element.click()
    element.press('Home')
    element.type(text)
    
    print(f"✅ Texto '{text}' insertado al inicio de: {selector}")

@step('tecleo "{key}" en el campo "{selector}"')
@step('que tecleo "{key}" en el campo "{selector}"')
def step_press_key_in_element(context, key, selector):
    """Presiona una tecla específica en un elemento"""
    # Obtener elemento
    if hasattr(context, 'get_element'):
        element = context.get_element(selector)
    else:
        element = context.page.locator(selector)
    
    # Hacer clic para enfocar y presionar tecla
    element.click()
    element.press(key)
    
    print(f"✅ Tecla '{key}' presionada en: {selector}")

@step('tecleo combinación "{key_combination}" en el campo "{selector}"')
@step('que tecleo combinación "{key_combination}" en el campo "{selector}"')
def step_press_key_combination_in_element(context, key_combination, selector):
    """Presiona una combinación de teclas en un elemento"""
    # Obtener elemento
    if hasattr(context, 'get_element'):
        element = context.get_element(selector)
    else:
        element = context.page.locator(selector)
    
    # Hacer clic para enfocar y presionar combinación
    element.click()
    element.press(key_combination)
    
    print(f"✅ Combinación '{key_combination}' presionada en: {selector}")

@step('enfoco el campo "{selector}"')
@step('que enfoco "{selector}"')
@step('hago foco en "{selector}"')
def step_focus_field(context, selector):
    """Enfoca un campo específico"""
    # Obtener elemento
    if hasattr(context, 'get_element'):
        element = context.get_element(selector)
    else:
        element = context.page.locator(selector)
    
    # Enfocar elemento
    element.focus()
    
    print(f"✅ Campo enfocado: {selector}")

@step('desenfocar el campo actual')
@step('que quito el foco del campo actual')
def step_blur_current_field(context):
    """Quita el foco del campo actual"""
    # Presionar Tab para mover el foco
    context.page.keyboard.press('Tab')
    print("✅ Foco removido del campo actual")

@step('copio el contenido del campo "{selector}" al portapapeles')
@step('que copio "{selector}" al portapapeles')
def step_copy_field_to_clipboard(context, selector):
    """Copia el contenido de un campo al portapapeles"""
    # Obtener elemento
    if hasattr(context, 'get_element'):
        element = context.get_element(selector)
    else:
        element = context.page.locator(selector)
    
    # Seleccionar todo y copiar
    element.click()
    element.press('Control+a')
    element.press('Control+c')
    
    print(f"✅ Contenido de '{selector}' copiado al portapapeles")

@step('pego el contenido del portapapeles en "{selector}"')
@step('que pego en "{selector}"')
def step_paste_from_clipboard(context, selector):
    """Pega el contenido del portapapeles en un campo"""
    # Obtener elemento
    if hasattr(context, 'get_element'):
        element = context.get_element(selector)
    else:
        element = context.page.locator(selector)
    
    # Hacer clic y pegar
    element.click()
    element.press('Control+v')
    
    print(f"✅ Contenido pegado en: {selector}")

@step('escribo avanzado "{text}" y presiono Enter en "{selector}"')
@step('que escribo avanzado "{text}" y presiono Enter en "{selector}"')
def step_type_and_enter_advanced(context, text, selector):
    """Escribe texto y presiona Enter"""
    # Resolver variables
    if hasattr(context, 'variable_manager'):
        text = context.variable_manager.resolve_variables(text)
    
    # Obtener elemento
    if hasattr(context, 'get_element'):
        element = context.get_element(selector)
    else:
        element = context.page.locator(selector)
    
    # Escribir texto y presionar Enter
    element.fill(text)
    element.press('Enter')
    
    print(f"✅ Texto '{text}' ingresado y Enter presionado en: {selector}")

@step('selecciono el texto desde la posición {start:d} hasta {end:d} en "{selector}"')
@step('que selecciono caracteres {start:d}-{end:d} en "{selector}"')
def step_select_text_range(context, start, end, selector):
    """Selecciona un rango específico de texto en un campo"""
    # Obtener elemento
    if hasattr(context, 'get_element'):
        element = context.get_element(selector)
    else:
        element = context.page.locator(selector)
    
    # Enfocar elemento
    element.click()
    
    # Usar JavaScript para seleccionar el rango
    context.page.evaluate(f"""
        const element = document.querySelector('{selector}');
        if (element && element.setSelectionRange) {{
            element.setSelectionRange({start}, {end});
        }}
    """)
    
    print(f"✅ Texto seleccionado desde posición {start} hasta {end} en: {selector}")

@step('escribo con velocidad "{speed_type}" el texto "{text}" en "{selector}"')
@step('que escribo con velocidad "{speed_type}" el texto "{text}" en "{selector}"')
def step_type_with_speed(context, text, speed_type, selector):
    """Escribe texto con diferentes velocidades predefinidas"""
    # Resolver variables
    if hasattr(context, 'variable_manager'):
        text = context.variable_manager.resolve_variables(text)
    
    # Definir velocidades (delay en ms)
    speeds = {
        'muy_lenta': 500,
        'lenta': 200,
        'normal': 100,
        'rapida': 50,
        'muy_rapida': 20
    }
    
    delay = speeds.get(speed_type.lower(), 100)  # Default: normal
    
    # Obtener elemento
    if hasattr(context, 'get_element'):
        element = context.get_element(selector)
    else:
        element = context.page.locator(selector)
    
    # Limpiar y escribir con velocidad específica
    element.click()
    element.clear()
    
    print(f"⌨️ Escribiendo '{text}' a velocidad {speed_type} en {selector}...")
    for char in text:
        element.type(char)
        time.sleep(delay / 1000)
    
    print(f"✅ Texto '{text}' ingresado a velocidad {speed_type} en: {selector}")

@step('simulo errores de escritura con texto "{text}" en "{selector}"')
@step('que escribo con errores simulados "{text}" en "{selector}"')
def step_type_with_errors(context, selector, text):
    """Simula errores de escritura humanos (escribir, borrar, corregir)"""
    # Resolver variables
    if hasattr(context, 'variable_manager'):
        text = context.variable_manager.resolve_variables(text)
    
    # Obtener elemento
    if hasattr(context, 'get_element'):
        element = context.get_element(selector)
    else:
        element = context.page.locator(selector)
    
    element.click()
    element.clear()
    
    print(f"⌨️ Escribiendo '{text}' con errores simulados en {selector}...")
    
    i = 0
    while i < len(text):
        char = text[i]
        
        # 15% de probabilidad de error
        if random.random() < 0.15 and i > 0:
            # Escribir carácter incorrecto
            wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
            element.type(wrong_char)
            time.sleep(random.randint(100, 300) / 1000)
            
            # Pausa (darse cuenta del error)
            time.sleep(random.randint(200, 500) / 1000)
            
            # Borrar carácter incorrecto
            element.press('Backspace')
            time.sleep(random.randint(50, 150) / 1000)
        
        # Escribir carácter correcto
        element.type(char)
        time.sleep(random.randint(80, 200) / 1000)
        
        i += 1
    
    print(f"✅ Texto '{text}' ingresado con errores simulados en: {selector}")

@step('verifico que puedo escribir en el campo "{selector}"')
@step('que verifico que "{selector}" acepta entrada de texto')
def step_verify_field_writable(context, selector):
    """Verifica que un campo acepta entrada de texto"""
    # Obtener elemento
    if hasattr(context, 'get_element'):
        element = context.get_element(selector)
    else:
        element = context.page.locator(selector)
    
    # Verificar que está habilitado y es editable
    assert element.is_enabled(), f"Campo '{selector}' no está habilitado"
    assert element.is_editable(), f"Campo '{selector}' no es editable"
    
    print(f"✅ Campo '{selector}' acepta entrada de texto")

@step('limpio el campo "{selector}" usando {method}')
@step('que limpio "{selector}" con método "{method}"')
def step_clear_field_with_method(context, selector, method):
    """Limpia un campo usando diferentes métodos"""
    # Obtener elemento
    if hasattr(context, 'get_element'):
        element = context.get_element(selector)
    else:
        element = context.page.locator(selector)
    
    element.click()
    
    if method.lower() == 'clear':
        element.clear()
    elif method.lower() == 'select_all':
        element.press('Control+a')
        element.press('Delete')
    elif method.lower() == 'backspace':
        # Obtener longitud del texto y borrar todo con backspace
        current_text = element.input_value()
        for _ in range(len(current_text)):
            element.press('Backspace')
    elif method.lower() == 'delete':
        element.press('Control+a')
        element.press('Delete')
    else:
        # Método por defecto
        element.clear()
    
    print(f"✅ Campo '{selector}' limpiado usando método: {method}")

@step('escribo texto multilínea en "{selector}"')
@step('que escribo múltiples líneas en "{selector}"')
def step_type_multiline_text(context, selector):
    """Escribe texto multilínea desde el contexto del step"""
    # El texto multilínea viene en context.text
    if not hasattr(context, 'text') or not context.text:
        raise ValueError("No se proporcionó texto multilínea. Use formato:\n\"\"\"\nTexto aquí\n\"\"\"")
    
    text = context.text.strip()
    
    # Resolver variables si están disponibles
    if hasattr(context, 'variable_manager'):
        text = context.variable_manager.resolve_variables(text)
    
    # Obtener elemento
    if hasattr(context, 'get_element'):
        element = context.get_element(selector)
    else:
        element = context.page.locator(selector)
    
    # Escribir texto multilínea
    element.click()
    element.clear()
    element.fill(text)
    
    lines_count = len(text.split('\n'))
    print(f"✅ Texto multilínea ({lines_count} líneas) ingresado en: {selector}")