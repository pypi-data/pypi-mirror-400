#!/usr/bin/env python3
"""
Steps para interacción con iFrames
"""
from behave import step
from playwright.sync_api import expect

@step('I switch to iframe "{iframe_name}" with identifier "{identifier}"')
@step('cambio al iframe "{iframe_name}" con identificador "{identifier}"')
def step_switch_to_iframe(context, iframe_name, identifier):
    """Cambia el contexto al iframe especificado"""
    locator = context.element_locator.get_locator(identifier)
    
    # Obtener el iframe
    iframe_element = context.page.locator(locator)
    expect(iframe_element).to_be_visible()
    
    # Cambiar al contenido del iframe
    context.current_frame = context.page.frame_locator(locator)
    
    # Guardar referencia para poder volver
    if not hasattr(context, 'frame_stack'):
        context.frame_stack = []
    context.frame_stack.append(context.current_frame)

@step('I switch to iframe by name "{name}"')
@step('cambio al iframe por nombre "{name}"')
def step_switch_to_iframe_by_name(context, name):
    """Cambia al iframe por su atributo name"""
    resolved_name = context.variable_manager.resolve_variables(name)
    
    # Buscar iframe por name
    iframe_locator = f'iframe[name="{resolved_name}"]'
    iframe_element = context.page.locator(iframe_locator)
    expect(iframe_element).to_be_visible()
    
    # Cambiar al contenido del iframe
    context.current_frame = context.page.frame_locator(iframe_locator)
    
    # Guardar referencia
    if not hasattr(context, 'frame_stack'):
        context.frame_stack = []
    context.frame_stack.append(context.current_frame)

@step('I switch to iframe by src containing "{src_part}"')
@step('cambio al iframe por src que contiene "{src_part}"')
def step_switch_to_iframe_by_src(context, src_part):
    """Cambia al iframe por parte de su URL src"""
    resolved_src = context.variable_manager.resolve_variables(src_part)
    
    # Buscar iframe por src
    iframe_locator = f'iframe[src*="{resolved_src}"]'
    iframe_element = context.page.locator(iframe_locator)
    expect(iframe_element).to_be_visible()
    
    # Cambiar al contenido del iframe
    context.current_frame = context.page.frame_locator(iframe_locator)
    
    # Guardar referencia
    if not hasattr(context, 'frame_stack'):
        context.frame_stack = []
    context.frame_stack.append(context.current_frame)

@step('I switch to iframe by index "{index}"')
@step('cambio al iframe por índice "{index}"')
def step_switch_to_iframe_by_index(context, index):
    """Cambia al iframe por su índice en la página"""
    iframe_index = int(index)
    
    # Obtener todos los iframes
    iframes = context.page.locator('iframe')
    iframe_count = iframes.count()
    
    assert iframe_index < iframe_count, f"Índice {iframe_index} fuera de rango. Solo hay {iframe_count} iframes"
    
    # Cambiar al iframe específico
    iframe_element = iframes.nth(iframe_index)
    expect(iframe_element).to_be_visible()
    
    # Usar el locator del iframe específico
    iframe_locator = f'iframe >> nth={iframe_index}'
    context.current_frame = context.page.frame_locator(iframe_locator)
    
    # Guardar referencia
    if not hasattr(context, 'frame_stack'):
        context.frame_stack = []
    context.frame_stack.append(context.current_frame)

@step('I switch back to parent frame')
@step('regreso al frame padre')
def step_switch_to_parent_frame(context):
    """Regresa al frame padre"""
    if hasattr(context, 'frame_stack') and context.frame_stack:
        # Remover el frame actual
        context.frame_stack.pop()
        
        # Si hay frames en el stack, usar el anterior
        if context.frame_stack:
            context.current_frame = context.frame_stack[-1]
        else:
            # Si no hay más frames, regresar a la página principal
            context.current_frame = None
    else:
        # Regresar a la página principal
        context.current_frame = None

@step('I switch to main content')
@step('regreso al contenido principal')
def step_switch_to_main_content(context):
    """Regresa al contenido principal de la página (fuera de todos los iframes)"""
    context.current_frame = None
    if hasattr(context, 'frame_stack'):
        context.frame_stack.clear()

@step('I click element "{element_name}" inside iframe with identifier "{identifier}"')
@step('hago click en el elemento "{element_name}" dentro del iframe con identificador "{identifier}"')
def step_click_element_in_iframe(context, element_name, identifier):
    """Hace click en un elemento dentro del iframe actual"""
    if not hasattr(context, 'current_frame') or context.current_frame is None:
        raise AssertionError("No hay iframe activo. Usa 'I switch to iframe' primero")
    
    locator = context.element_locator.get_locator(identifier)
    context.current_frame.locator(locator).click()

@step('I fill field "{field_name}" with "{text}" inside iframe with identifier "{identifier}"')
@step('relleno el campo "{field_name}" con "{text}" dentro del iframe con identificador "{identifier}"')
def step_fill_field_in_iframe(context, field_name, text, identifier):
    """Rellena un campo dentro del iframe actual"""
    if not hasattr(context, 'current_frame') or context.current_frame is None:
        raise AssertionError("No hay iframe activo. Usa 'I switch to iframe' primero")
    
    locator = context.element_locator.get_locator(identifier)
    resolved_text = context.variable_manager.resolve_variables(text)
    context.current_frame.locator(locator).fill(resolved_text)

@step('I should see text "{text}" inside iframe')
@step('debería ver el texto "{text}" dentro del iframe')
def step_should_see_text_in_iframe(context, text):
    """Verifica que un texto sea visible dentro del iframe actual"""
    if not hasattr(context, 'current_frame') or context.current_frame is None:
        raise AssertionError("No hay iframe activo. Usa 'I switch to iframe' primero")
    
    resolved_text = context.variable_manager.resolve_variables(text)
    expect(context.current_frame.locator(f'text="{resolved_text}"')).to_be_visible()

@step('I should see element "{element_name}" inside iframe with identifier "{identifier}"')
@step('debería ver el elemento "{element_name}" dentro del iframe con identificador "{identifier}"')
def step_should_see_element_in_iframe(context, element_name, identifier):
    """Verifica que un elemento sea visible dentro del iframe actual"""
    if not hasattr(context, 'current_frame') or context.current_frame is None:
        raise AssertionError("No hay iframe activo. Usa 'I switch to iframe' primero")
    
    locator = context.element_locator.get_locator(identifier)
    expect(context.current_frame.locator(locator)).to_be_visible()

@step('I wait for iframe "{iframe_name}" to load with identifier "{identifier}"')
@step('espero a que cargue el iframe "{iframe_name}" con identificador "{identifier}"')
def step_wait_for_iframe_load(context, iframe_name, identifier):
    """Espera a que un iframe termine de cargar"""
    locator = context.element_locator.get_locator(identifier)
    
    # Esperar a que el iframe sea visible
    iframe_element = context.page.locator(locator)
    expect(iframe_element).to_be_visible()
    
    # Esperar a que el iframe termine de cargar
    context.page.wait_for_load_state('networkidle')

@step('I execute javascript "{script}" inside iframe')
@step('ejecuto javascript "{script}" dentro del iframe')
def step_execute_javascript_in_iframe(context, script):
    """Ejecuta JavaScript dentro del iframe actual"""
    if not hasattr(context, 'current_frame') or context.current_frame is None:
        raise AssertionError("No hay iframe activo. Usa 'I switch to iframe' primero")
    
    resolved_script = context.variable_manager.resolve_variables(script)
    
    # Ejecutar JavaScript en el contexto del iframe
    result = context.page.evaluate(f"""
        () => {{
            const iframe = document.querySelector('iframe');
            if (iframe && iframe.contentWindow) {{
                return iframe.contentWindow.eval(`{resolved_script}`);
            }}
            return null;
        }}
    """)
    
    return result

@step('I get iframe count and store in variable "{variable_name}"')
@step('obtengo el número de iframes y lo guardo en la variable "{variable_name}"')
def step_get_iframe_count(context, variable_name):
    """Obtiene el número total de iframes en la página"""
    iframe_count = context.page.locator('iframe').count()
    context.variable_manager.set_variable(variable_name, iframe_count)

@step('I verify iframe "{iframe_name}" exists with identifier "{identifier}"')
@step('verifico que existe el iframe "{iframe_name}" con identificador "{identifier}"')
def step_verify_iframe_exists(context, iframe_name, identifier):
    """Verifica que un iframe existe en la página"""
    locator = context.element_locator.get_locator(identifier)
    expect(context.page.locator(locator)).to_be_visible()

@step('I verify iframe "{iframe_name}" has src "{expected_src}" with identifier "{identifier}"')
@step('verifico que el iframe "{iframe_name}" tiene src "{expected_src}" con identificador "{identifier}"')
def step_verify_iframe_src(context, iframe_name, expected_src, identifier):
    """Verifica que un iframe tiene una URL src específica"""
    locator = context.element_locator.get_locator(identifier)
    resolved_src = context.variable_manager.resolve_variables(expected_src)
    
    iframe_element = context.page.locator(locator)
    actual_src = iframe_element.get_attribute('src')
    
    assert resolved_src in actual_src, f"iframe src '{actual_src}' no contiene '{resolved_src}'"