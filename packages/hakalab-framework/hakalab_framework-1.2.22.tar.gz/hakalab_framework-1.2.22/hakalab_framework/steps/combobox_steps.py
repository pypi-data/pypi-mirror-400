#!/usr/bin/env python3
"""
Steps para interacción avanzada con combobox, select y dropdowns
"""
from behave import step
from playwright.sync_api import expect
import time

@step('I select option "{option}" from combobox "{element_name}" with identifier "{identifier}"')
@step('selecciono la opción "{option}" del combobox "{element_name}" con identificador "{identifier}"')
def step_select_combobox_option(context, option, element_name, identifier):
    """Selecciona una opción de un combobox/select por texto visible"""
    locator = context.element_locator.get_locator(identifier)
    resolved_option = context.variable_manager.resolve_variables(option)
    
    # Intentar diferentes métodos de selección
    try:
        # Método 1: Select nativo
        context.page.locator(locator).select_option(label=resolved_option)
    except:
        try:
            # Método 2: Select por valor
            context.page.locator(locator).select_option(value=resolved_option)
        except:
            # Método 3: Click y buscar opción
            context.page.locator(locator).click()
            context.page.locator(f'option:has-text("{resolved_option}")').click()

@step('I select option by value "{value}" from combobox "{element_name}" with identifier "{identifier}"')
@step('selecciono la opción por valor "{value}" del combobox "{element_name}" con identificador "{identifier}"')
def step_select_combobox_by_value(context, value, element_name, identifier):
    """Selecciona una opción de un combobox/select por valor"""
    locator = context.element_locator.get_locator(identifier)
    resolved_value = context.variable_manager.resolve_variables(value)
    context.page.locator(locator).select_option(value=resolved_value)

@step('I select option by index "{index}" from combobox "{element_name}" with identifier "{identifier}"')
@step('selecciono la opción por índice "{index}" del combobox "{element_name}" con identificador "{identifier}"')
def step_select_combobox_by_index(context, index, element_name, identifier):
    """Selecciona una opción de un combobox/select por índice"""
    locator = context.element_locator.get_locator(identifier)
    option_index = int(index)
    context.page.locator(locator).select_option(index=option_index)

@step('I open dropdown "{element_name}" with identifier "{identifier}"')
@step('abro el dropdown "{element_name}" con identificador "{identifier}"')
def step_open_dropdown(context, element_name, identifier):
    """Abre un dropdown personalizado"""
    locator = context.element_locator.get_locator(identifier)
    context.page.locator(locator).click()
    
    # Esperar a que aparezcan las opciones
    time.sleep(0.5)

@step('I select dropdown option "{option}" from opened dropdown')
@step('selecciono la opción "{option}" del dropdown abierto')
def step_select_dropdown_option(context, option):
    """Selecciona una opción de un dropdown abierto"""
    resolved_option = context.variable_manager.resolve_variables(option)
    
    # Buscar la opción por diferentes métodos
    selectors = [
        f'[role="option"]:has-text("{resolved_option}")',
        f'.dropdown-option:has-text("{resolved_option}")',
        f'.option:has-text("{resolved_option}")',
        f'li:has-text("{resolved_option}")',
        f'div:has-text("{resolved_option}")'
    ]
    
    for selector in selectors:
        try:
            if context.page.locator(selector).count() > 0:
                context.page.locator(selector).first.click()
                return
        except:
            continue
    
    # Si no encuentra la opción, intentar con texto exacto
    context.page.get_by_text(resolved_option, exact=True).click()

@step('I type and select "{text}" in searchable combobox "{element_name}" with identifier "{identifier}"')
@step('escribo y selecciono "{text}" en el combobox buscable "{element_name}" con identificador "{identifier}"')
def step_type_and_select_combobox(context, text, element_name, identifier):
    """Escribe en un combobox buscable y selecciona la opción"""
    locator = context.element_locator.get_locator(identifier)
    resolved_text = context.variable_manager.resolve_variables(text)
    
    # Hacer click para abrir el combobox
    context.page.locator(locator).click()
    
    # Escribir el texto
    context.page.locator(locator).fill(resolved_text)
    
    # Esperar a que aparezcan las opciones filtradas
    time.sleep(1)
    
    # Seleccionar la primera opción que coincida
    try:
        context.page.locator(f'[role="option"]:has-text("{resolved_text}")').first.click()
    except:
        # Presionar Enter como alternativa
        context.page.locator(locator).press('Enter')

@step('I clear combobox selection "{element_name}" with identifier "{identifier}"')
@step('limpio la selección del combobox "{element_name}" con identificador "{identifier}"')
def step_clear_combobox(context, element_name, identifier):
    """Limpia la selección de un combobox"""
    locator = context.element_locator.get_locator(identifier)
    
    # Intentar diferentes métodos de limpieza
    try:
        # Método 1: Seleccionar opción vacía
        context.page.locator(locator).select_option(value="")
    except:
        try:
            # Método 2: Buscar botón de limpiar
            clear_button = context.page.locator(f'{locator} + .clear-button, {locator} .clear-icon')
            if clear_button.count() > 0:
                clear_button.click()
        except:
            # Método 3: Limpiar como campo de texto
            context.page.locator(locator).fill("")

@step('I verify combobox "{element_name}" has selected option "{option}" with identifier "{identifier}"')
@step('verifico que el combobox "{element_name}" tiene seleccionada la opción "{option}" con identificador "{identifier}"')
def step_verify_combobox_selection(context, element_name, option, identifier):
    """Verifica que un combobox tiene una opción específica seleccionada"""
    locator = context.element_locator.get_locator(identifier)
    resolved_option = context.variable_manager.resolve_variables(option)
    
    # Verificar por valor seleccionado
    selected_value = context.page.locator(locator).input_value()
    assert selected_value == resolved_option, f"Combobox tiene '{selected_value}', esperado '{resolved_option}'"

@step('I verify combobox "{element_name}" contains options "{options}" with identifier "{identifier}"')
@step('verifico que el combobox "{element_name}" contiene las opciones "{options}" con identificador "{identifier}"')
def step_verify_combobox_options(context, element_name, options, identifier):
    """Verifica que un combobox contiene opciones específicas"""
    locator = context.element_locator.get_locator(identifier)
    expected_options = [opt.strip() for opt in options.split(',')]
    
    # Obtener todas las opciones del select
    option_elements = context.page.locator(f'{locator} option')
    actual_options = []
    
    for i in range(option_elements.count()):
        option_text = option_elements.nth(i).text_content()
        if option_text.strip():  # Ignorar opciones vacías
            actual_options.append(option_text.strip())
    
    # Verificar que todas las opciones esperadas están presentes
    for expected_option in expected_options:
        assert expected_option in actual_options, f"Opción '{expected_option}' no encontrada. Opciones disponibles: {actual_options}"

@step('I select multiple options "{options}" from multiselect "{element_name}" with identifier "{identifier}"')
@step('selecciono múltiples opciones "{options}" del multiselect "{element_name}" con identificador "{identifier}"')
def step_select_multiple_options(context, options, element_name, identifier):
    """Selecciona múltiples opciones de un select múltiple"""
    locator = context.element_locator.get_locator(identifier)
    option_list = [opt.strip() for opt in options.split(',')]
    
    # Seleccionar múltiples opciones
    for option in option_list:
        resolved_option = context.variable_manager.resolve_variables(option)
        context.page.locator(locator).select_option(label=resolved_option)

@step('I navigate combobox options with arrow keys and select option "{option}" from "{element_name}" with identifier "{identifier}"')
@step('navego las opciones del combobox con flechas y selecciono la opción "{option}" de "{element_name}" con identificador "{identifier}"')
def step_navigate_combobox_with_keys(context, option, element_name, identifier):
    """Navega por las opciones de un combobox usando teclas de flecha"""
    locator = context.element_locator.get_locator(identifier)
    resolved_option = context.variable_manager.resolve_variables(option)
    
    # Hacer focus en el combobox
    context.page.locator(locator).focus()
    
    # Abrir dropdown con flecha hacia abajo
    context.page.locator(locator).press('ArrowDown')
    
    # Navegar hasta encontrar la opción deseada
    max_attempts = 20
    for _ in range(max_attempts):
        # Obtener texto de la opción actual
        try:
            current_option = context.page.evaluate("""
                (selector) => {
                    const element = document.querySelector(selector);
                    return element.options[element.selectedIndex].text;
                }
            """, locator)
            
            if current_option == resolved_option:
                # Presionar Enter para seleccionar
                context.page.locator(locator).press('Enter')
                return
            
            # Continuar navegando
            context.page.locator(locator).press('ArrowDown')
        except:
            context.page.locator(locator).press('ArrowDown')
    
    raise AssertionError(f"No se pudo encontrar la opción '{resolved_option}' navegando con flechas")