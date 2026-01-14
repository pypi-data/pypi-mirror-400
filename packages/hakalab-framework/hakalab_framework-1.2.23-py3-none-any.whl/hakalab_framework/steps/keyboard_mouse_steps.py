#!/usr/bin/env python3
"""
Steps para interacciones avanzadas de teclado y mouse
"""
from behave import step
import time

@step('I press key "{key}"')
@step('pulso la tecla "{key}"')
def step_press_key(context, key):
    """Presiona una tecla específica"""
    resolved_key = context.variable_manager.resolve_variables(key)
    context.page.keyboard.press(resolved_key)

@step('I press key combination "{keys}"')
@step('presiono la combinación de teclas "{keys}"')
def step_press_key_combination(context, keys):
    """Presiona una combinación de teclas (ej: Ctrl+C, Alt+Tab)"""
    resolved_keys = context.variable_manager.resolve_variables(keys)
    
    # Separar las teclas por + y presionar en secuencia
    key_parts = [k.strip() for k in resolved_keys.split('+')]
    
    if len(key_parts) == 1:
        context.page.keyboard.press(key_parts[0])
    else:
        # Presionar teclas modificadoras
        for key in key_parts[:-1]:
            context.page.keyboard.down(key)
        
        # Presionar tecla final
        context.page.keyboard.press(key_parts[-1])
        
        # Soltar teclas modificadoras en orden inverso
        for key in reversed(key_parts[:-1]):
            context.page.keyboard.up(key)

@step('I type text "{text}" with delay "{delay}" ms between characters')
@step('escribo el texto "{text}" con retraso de "{delay}" ms entre caracteres')
def step_type_with_delay(context, text, delay):
    """Escribe texto con retraso entre caracteres"""
    resolved_text = context.variable_manager.resolve_variables(text)
    delay_ms = int(delay)
    
    for char in resolved_text:
        context.page.keyboard.type(char)
        time.sleep(delay_ms / 1000.0)

@step('I hold key "{key}" for "{duration}" seconds')
@step('mantengo presionada la tecla "{key}" por "{duration}" segundos')
def step_hold_key(context, key, duration):
    """Mantiene presionada una tecla por un tiempo específico"""
    resolved_key = context.variable_manager.resolve_variables(key)
    duration_seconds = float(duration)
    
    context.page.keyboard.down(resolved_key)
    time.sleep(duration_seconds)
    context.page.keyboard.up(resolved_key)

@step('I click at coordinates x="{x}" y="{y}"')
@step('hago click en las coordenadas x="{x}" y="{y}"')
def step_click_coordinates(context, x, y):
    """Hace click en coordenadas específicas"""
    x_coord = int(x)
    y_coord = int(y)
    context.page.mouse.click(x_coord, y_coord)

@step('I double click at coordinates x="{x}" y="{y}"')
@step('hago doble click en las coordenadas x="{x}" y="{y}"')
def step_double_click_coordinates(context, x, y):
    """Hace doble click en coordenadas específicas"""
    x_coord = int(x)
    y_coord = int(y)
    context.page.mouse.dblclick(x_coord, y_coord)

@step('I right click at coordinates x="{x}" y="{y}"')
@step('hago click derecho en las coordenadas x="{x}" y="{y}"')
def step_right_click_coordinates(context, x, y):
    """Hace click derecho en coordenadas específicas"""
    x_coord = int(x)
    y_coord = int(y)
    context.page.mouse.click(x_coord, y_coord, button='right')

@step('I move mouse to coordinates x="{x}" y="{y}"')
@step('muevo el mouse a las coordenadas x="{x}" y="{y}"')
def step_move_mouse(context, x, y):
    """Mueve el mouse a coordenadas específicas"""
    x_coord = int(x)
    y_coord = int(y)
    context.page.mouse.move(x_coord, y_coord)

@step('I scroll mouse wheel "{direction}" by "{steps}" steps')
@step('hago scroll con la rueda del mouse "{direction}" por "{steps}" pasos')
def step_scroll_wheel(context, direction, steps):
    """Hace scroll con la rueda del mouse"""
    step_count = int(steps)
    
    if direction.lower() == 'up':
        delta_y = -step_count * 120  # Scroll hacia arriba
    elif direction.lower() == 'down':
        delta_y = step_count * 120   # Scroll hacia abajo
    else:
        raise ValueError(f"Dirección no válida: {direction}. Use 'up' o 'down'")
    
    context.page.mouse.wheel(0, delta_y)

@step('I perform mouse gesture from x="{start_x}" y="{start_y}" to x="{end_x}" y="{end_y}"')
@step('realizo gesto de mouse desde x="{start_x}" y="{start_y}" hasta x="{end_x}" y="{end_y}"')
def step_mouse_gesture(context, start_x, start_y, end_x, end_y):
    """Realiza un gesto de mouse desde un punto hasta otro"""
    start_x_coord = int(start_x)
    start_y_coord = int(start_y)
    end_x_coord = int(end_x)
    end_y_coord = int(end_y)
    
    # Mover a posición inicial
    context.page.mouse.move(start_x_coord, start_y_coord)
    
    # Presionar botón del mouse
    context.page.mouse.down()
    
    # Mover a posición final
    context.page.mouse.move(end_x_coord, end_y_coord)
    
    # Soltar botón del mouse
    context.page.mouse.up()

@step('I simulate keyboard shortcut "{shortcut}" on element "{element_name}" with identifier "{identifier}"')
@step('simulo el atajo de teclado "{shortcut}" en el elemento "{element_name}" con identificador "{identifier}"')
def step_keyboard_shortcut_on_element(context, shortcut, element_name, identifier):
    """Simula un atajo de teclado en un elemento específico"""
    locator = context.element_locator.get_locator(identifier)
    resolved_shortcut = context.variable_manager.resolve_variables(shortcut)
    
    # Hacer focus en el elemento
    context.page.locator(locator).focus()
    
    # Presionar atajo de teclado
    context.page.locator(locator).press(resolved_shortcut)

@step('I select all text with Ctrl+A')
@step('selecciono todo el texto con Ctrl+A')
def step_select_all(context):
    """Selecciona todo el texto con Ctrl+A"""
    context.page.keyboard.press('Control+a')

@step('I copy selected text with Ctrl+C')
@step('copio el texto seleccionado con Ctrl+C')
def step_copy_text(context):
    """Copia el texto seleccionado con Ctrl+C"""
    context.page.keyboard.press('Control+c')

@step('I paste text with Ctrl+V')
@step('pego el texto con Ctrl+V')
def step_paste_text(context):
    """Pega texto con Ctrl+V"""
    context.page.keyboard.press('Control+v')

@step('I cut text with Ctrl+X')
@step('corto el texto con Ctrl+X')
def step_cut_text(context):
    """Corta texto con Ctrl+X"""
    context.page.keyboard.press('Control+x')

@step('I undo action with Ctrl+Z')
@step('deshago la acción con Ctrl+Z')
def step_undo(context):
    """Deshace la última acción con Ctrl+Z"""
    context.page.keyboard.press('Control+z')

@step('I redo action with Ctrl+Y')
@step('rehago la acción con Ctrl+Y')
def step_redo(context):
    """Rehace la acción con Ctrl+Y"""
    context.page.keyboard.press('Control+y')

@step('I navigate with Tab key "{times}" times')
@step('navego con la tecla Tab "{times}" veces')
def step_navigate_tab(context, times):
    """Navega usando la tecla Tab un número específico de veces"""
    tab_count = int(times)
    
    for _ in range(tab_count):
        context.page.keyboard.press('Tab')

@step('I navigate with Shift+Tab "{times}" times')
@step('navego con Shift+Tab "{times}" veces')
def step_navigate_shift_tab(context, times):
    """Navega hacia atrás usando Shift+Tab"""
    tab_count = int(times)
    
    for _ in range(tab_count):
        context.page.keyboard.press('Shift+Tab')

@step('I press Enter key')
@step('pulso la tecla Enter')
def step_press_enter(context):
    """Presiona la tecla Enter"""
    context.page.keyboard.press('Enter')

@step('I press Escape key')
@step('presiono la tecla Escape')
def step_press_escape(context):
    """Presiona la tecla Escape"""
    context.page.keyboard.press('Escape')

@step('I press Space key')
@step('presiono la tecla Espacio')
def step_press_space(context):
    """Presiona la tecla Espacio"""
    context.page.keyboard.press('Space')

@step('I press arrow key "{direction}"')
@step('presiono la tecla de flecha "{direction}"')
def step_press_arrow(context, direction):
    """Presiona una tecla de flecha específica"""
    arrow_keys = {
        'up': 'ArrowUp',
        'down': 'ArrowDown', 
        'left': 'ArrowLeft',
        'right': 'ArrowRight',
        'arriba': 'ArrowUp',
        'abajo': 'ArrowDown',
        'izquierda': 'ArrowLeft',
        'derecha': 'ArrowRight'
    }
    
    key = arrow_keys.get(direction.lower())
    if not key:
        raise ValueError(f"Dirección no válida: {direction}. Use: up, down, left, right")
    
    context.page.keyboard.press(key)

@step('I type text "{text}" and press Enter')
@step('escribo el texto "{text}" y presiono Enter')
def step_type_and_enter(context, text):
    """Escribe texto y presiona Enter"""
    resolved_text = context.variable_manager.resolve_variables(text)
    context.page.keyboard.type(resolved_text)
    context.page.keyboard.press('Enter')

@step('I clear current field with Ctrl+A and Delete')
@step('limpio el campo actual con Ctrl+A y Delete')
def step_clear_field_keyboard(context):
    """Limpia el campo actual seleccionando todo y borrando"""
    context.page.keyboard.press('Control+a')
    context.page.keyboard.press('Delete')

@step('I simulate typing like human with text "{text}" and random delays')
@step('simulo escritura humana con el texto "{text}" y retrasos aleatorios')
def step_human_typing(context, text):
    """Simula escritura humana con retrasos aleatorios entre caracteres"""
    import random
    
    resolved_text = context.variable_manager.resolve_variables(text)
    
    for char in resolved_text:
        context.page.keyboard.type(char)
        # Retraso aleatorio entre 50-200ms
        delay = random.uniform(0.05, 0.2)
        time.sleep(delay)