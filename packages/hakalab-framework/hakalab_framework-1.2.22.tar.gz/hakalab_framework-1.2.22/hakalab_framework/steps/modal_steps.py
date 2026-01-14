#!/usr/bin/env python3
"""
Steps para interacción con modales y diálogos
"""
from behave import step
from playwright.sync_api import expect
import time
import os

@step('I wait for modal "{modal_name}" to appear with identifier "{identifier}"')
@step('espero a que aparezca el modal "{modal_name}" con identificador "{identifier}"')
def step_wait_for_modal(context, modal_name, identifier):
    """Espera a que aparezca un modal"""
    locator = context.element_locator.get_locator(identifier)
    expect(context.page.locator(locator)).to_be_visible(timeout=10000)

@step('I wait for modal "{modal_name}" to disappear with identifier "{identifier}"')
@step('espero a que desaparezca el modal "{modal_name}" con identificador "{identifier}"')
def step_wait_for_modal_disappear(context, modal_name, identifier):
    """Espera a que desaparezca un modal"""
    locator = context.element_locator.get_locator(identifier)
    expect(context.page.locator(locator)).not_to_be_visible(timeout=10000)

@step('I close modal "{modal_name}" by clicking close button with identifier "{identifier}"')
@step('cierro el modal "{modal_name}" haciendo click en el botón cerrar con identificador "{identifier}"')
def step_close_modal_by_button(context, modal_name, identifier):
    """Cierra un modal haciendo click en el botón de cerrar"""
    locator = context.element_locator.get_locator(identifier)
    context.page.locator(locator).click()

@step('I close modal by pressing Escape key')
@step('cierro el modal presionando la tecla Escape')
def step_close_modal_escape(context):
    """Cierra un modal presionando la tecla Escape"""
    context.page.keyboard.press('Escape')

@step('I close modal by clicking outside')
@step('cierro el modal haciendo click fuera')
def step_close_modal_outside(context):
    """Cierra un modal haciendo click fuera del contenido del modal"""
    # Hacer click en las coordenadas 10,10 (esquina superior izquierda)
    context.page.mouse.click(10, 10)

@step('I verify modal "{modal_name}" is visible with identifier "{identifier}"')
@step('verifico que el modal "{modal_name}" es visible con identificador "{identifier}"')
def step_verify_modal_visible(context, modal_name, identifier):
    """Verifica que un modal es visible"""
    locator = context.element_locator.get_locator(identifier)
    expect(context.page.locator(locator)).to_be_visible()

@step('I verify modal "{modal_name}" is not visible with identifier "{identifier}"')
@step('verifico que el modal "{modal_name}" no es visible con identificador "{identifier}"')
def step_verify_modal_not_visible(context, modal_name, identifier):
    """Verifica que un modal no es visible"""
    locator = context.element_locator.get_locator(identifier)
    expect(context.page.locator(locator)).not_to_be_visible()

@step('I verify modal "{modal_name}" has title "{expected_title}" with identifier "{identifier}"')
@step('verifico que el modal "{modal_name}" tiene el título "{expected_title}" con identificador "{identifier}"')
def step_verify_modal_title(context, modal_name, expected_title, identifier):
    """Verifica que un modal tiene un título específico"""
    locator = context.element_locator.get_locator(identifier)
    resolved_title = context.variable_manager.resolve_variables(expected_title)
    
    # Buscar el título dentro del modal
    modal_element = context.page.locator(locator)
    title_selectors = [
        '.modal-title',
        '.modal-header h1',
        '.modal-header h2',
        '.modal-header h3',
        'h1', 'h2', 'h3'
    ]
    
    title_found = False
    for selector in title_selectors:
        title_element = modal_element.locator(selector)
        if title_element.count() > 0:
            actual_title = title_element.text_content()
            if resolved_title in actual_title:
                title_found = True
                break
    
    assert title_found, f"Título '{resolved_title}' no encontrado en el modal"

@step('I click button "{button_text}" in modal "{modal_name}" with modal identifier "{modal_id}"')
@step('hago click en el botón "{button_text}" del modal "{modal_name}" con identificador de modal "{modal_id}"')
def step_click_button_in_modal(context, button_text, modal_name, modal_id):
    """Hace click en un botón específico dentro de un modal"""
    modal_locator = context.element_locator.get_locator(modal_id)
    resolved_button_text = context.variable_manager.resolve_variables(button_text)
    
    # Buscar el botón dentro del modal
    modal_element = context.page.locator(modal_locator)
    button_selectors = [
        f'button:has-text("{resolved_button_text}")',
        f'input[type="button"][value="{resolved_button_text}"]',
        f'input[type="submit"][value="{resolved_button_text}"]',
        f'a:has-text("{resolved_button_text}")',
        f'[role="button"]:has-text("{resolved_button_text}")'
    ]
    
    button_clicked = False
    for selector in button_selectors:
        button_element = modal_element.locator(selector)
        if button_element.count() > 0:
            button_element.first.click()
            button_clicked = True
            break
    
    assert button_clicked, f"Botón '{resolved_button_text}' no encontrado en el modal"

@step('I fill field "{field_name}" with "{text}" in modal "{modal_name}" with identifiers modal="{modal_id}" field="{field_id}"')
@step('relleno el campo "{field_name}" con "{text}" en el modal "{modal_name}" con identificadores modal="{modal_id}" campo="{field_id}"')
def step_fill_field_in_modal(context, field_name, text, modal_name, modal_id, field_id):
    """Rellena un campo dentro de un modal"""
    modal_locator = context.element_locator.get_locator(modal_id)
    field_locator = context.element_locator.get_locator(field_id)
    resolved_text = context.variable_manager.resolve_variables(text)
    
    # Buscar el campo dentro del modal
    modal_element = context.page.locator(modal_locator)
    field_element = modal_element.locator(field_locator)
    
    expect(field_element).to_be_visible()
    field_element.fill(resolved_text)

@step('I verify modal "{modal_name}" contains text "{text}" with identifier "{identifier}"')
@step('verifico que el modal "{modal_name}" contiene el texto "{text}" con identificador "{identifier}"')
def step_verify_modal_contains_text(context, modal_name, text, identifier):
    """Verifica que un modal contiene un texto específico"""
    modal_locator = context.element_locator.get_locator(identifier)
    resolved_text = context.variable_manager.resolve_variables(text)
    
    modal_element = context.page.locator(modal_locator)
    expect(modal_element.locator(f'text="{resolved_text}"')).to_be_visible()

@step('I handle browser alert with action "{action}"')
@step('manejo la alerta del navegador con acción "{action}"')
def step_handle_browser_alert(context, action):
    """Maneja alertas del navegador (accept/dismiss)"""
    
    def handle_dialog(dialog):
        if action.lower() == 'accept':
            dialog.accept()
        elif action.lower() == 'dismiss':
            dialog.dismiss()
        else:
            raise ValueError(f"Acción no válida: {action}. Use 'accept' o 'dismiss'")
    
    # Configurar el manejador de diálogos
    context.page.on('dialog', handle_dialog)

@step('I handle browser confirm with action "{action}"')
@step('manejo la confirmación del navegador con acción "{action}"')
def step_handle_browser_confirm(context, action):
    """Maneja confirmaciones del navegador (accept/dismiss)"""
    step_handle_browser_alert(context, action)

@step('I handle browser prompt with text "{text}" and action "{action}"')
@step('manejo el prompt del navegador con texto "{text}" y acción "{action}"')
def step_handle_browser_prompt(context, text, action):
    """Maneja prompts del navegador con texto y acción"""
    resolved_text = context.variable_manager.resolve_variables(text)
    
    def handle_dialog(dialog):
        if action.lower() == 'accept':
            dialog.accept(resolved_text)
        elif action.lower() == 'dismiss':
            dialog.dismiss()
        else:
            raise ValueError(f"Acción no válida: {action}. Use 'accept' o 'dismiss'")
    
    # Configurar el manejador de diálogos
    context.page.on('dialog', handle_dialog)

@step('I wait for any modal to appear')
@step('espero a que aparezca cualquier modal')
def step_wait_for_any_modal(context):
    """Espera a que aparezca cualquier modal en la página"""
    modal_selectors = [
        '.modal',
        '.dialog',
        '.popup',
        '[role="dialog"]',
        '.overlay',
        '.modal-overlay'
    ]
    
    modal_appeared = False
    for selector in modal_selectors:
        try:
            context.page.wait_for_selector(selector, state='visible', timeout=5000)
            modal_appeared = True
            break
        except:
            continue
    
    assert modal_appeared, "No apareció ningún modal en el tiempo esperado"

@step('I verify no modals are visible')
@step('verifico que no hay modales visibles')
def step_verify_no_modals_visible(context):
    """Verifica que no hay modales visibles en la página"""
    modal_selectors = [
        '.modal',
        '.dialog',
        '.popup',
        '[role="dialog"]',
        '.overlay',
        '.modal-overlay'
    ]
    
    for selector in modal_selectors:
        modal_elements = context.page.locator(selector)
        if modal_elements.count() > 0:
            # Verificar que ninguno es visible
            for i in range(modal_elements.count()):
                expect(modal_elements.nth(i)).not_to_be_visible()

@step('I take screenshot of modal "{modal_name}" with identifier "{identifier}"')
@step('tomo captura del modal "{modal_name}" con identificador "{identifier}"')
def step_screenshot_modal(context, modal_name, identifier):
    """Toma una captura de pantalla específica del modal"""
    modal_locator = context.element_locator.get_locator(identifier)
    modal_element = context.page.locator(modal_locator)
    
    # Generar nombre de archivo
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"modal_{modal_name}_{timestamp}.png"
    
    # Obtener directorio de screenshots desde variables de entorno
    screenshots_dir = os.getenv('SCREENSHOTS_DIR', 'screenshots')
    
    # Tomar screenshot del modal específico
    modal_element.screenshot(path=f"{screenshots_dir}/{filename}")
    print(f"📸 Screenshot del modal guardado: {screenshots_dir}/{filename}")