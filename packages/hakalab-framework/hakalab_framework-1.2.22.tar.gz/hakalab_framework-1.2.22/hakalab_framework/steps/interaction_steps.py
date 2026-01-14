from behave import step
from playwright.sync_api import TimeoutError

@step('I click on the element "{element_name}" with identifier "{identifier}"')
@step('hago click en el elemento "{element_name}" con identificador "{identifier}"')
@step('que hago click en el elemento "{element_name}" con identificador "{identifier}"')
def step_click_element(context, element_name, identifier):
    """Hace click en un elemento"""
    locator = context.element_locator.get_locator(identifier)
    context.page.click(locator)

@step('I double click on the element "{element_name}" with identifier "{identifier}"')
@step('hago doble click en el elemento "{element_name}" con identificador "{identifier}"')
@step('que hago doble click en el elemento "{element_name}" con identificador "{identifier}"')
def step_double_click_element(context, element_name, identifier):
    """Hace doble click en un elemento"""
    locator = context.element_locator.get_locator(identifier)
    context.page.dblclick(locator)

@step('I right click on the element "{element_name}" with identifier "{identifier}"')
@step('hago click derecho en el elemento "{element_name}" con identificador "{identifier}"')
@step('que hago click derecho en el elemento "{element_name}" con identificador "{identifier}"')
def step_right_click_element(context, element_name, identifier):
    """Hace click derecho en un elemento"""
    locator = context.element_locator.get_locator(identifier)
    context.page.click(locator, button='right')

@step('I hover over the element "{element_name}" with identifier "{identifier}"')
@step('paso el mouse sobre el elemento "{element_name}" con identificador "{identifier}"')
@step('que paso el mouse sobre el elemento "{element_name}" con identificador "{identifier}"')
def step_hover_element(context, element_name, identifier):
    """Pasa el mouse sobre un elemento"""
    locator = context.element_locator.get_locator(identifier)
    context.page.hover(locator)

@step('I fill the field "{field_name}" with "{text}" with identifier "{identifier}"')
@step('relleno el campo "{field_name}" con "{text}" con identificador "{identifier}"')
@step('que relleno el campo "{field_name}" con "{text}" con identificador "{identifier}"')
def step_fill_field(context, field_name, text, identifier):
    """Rellena un campo de texto"""
    locator = context.element_locator.get_locator(identifier)
    resolved_text = context.variable_manager.resolve_variables(text)
    context.page.fill(locator, resolved_text)

@step('I clear the field "{field_name}" with identifier "{identifier}"')
@step('limpio el campo "{field_name}" con identificador "{identifier}"')
@step('que limpio el campo "{field_name}" con identificador "{identifier}"')
def step_clear_field(context, field_name, identifier):
    """Limpia un campo de texto"""
    locator = context.element_locator.get_locator(identifier)
    context.page.fill(locator, '')

@step('I type "{text}" in the field "{field_name}" with identifier "{identifier}"')
@step('escribo "{text}" en el campo "{field_name}" con identificador "{identifier}"')
@step('que escribo "{text}" en el campo "{field_name}" con identificador "{identifier}"')
def step_type_in_field(context, text, field_name, identifier):
    """Escribe texto en un campo (sin limpiar primero)"""
    locator = context.element_locator.get_locator(identifier)
    resolved_text = context.variable_manager.resolve_variables(text)
    context.page.type(locator, resolved_text)

@step('I select the option "{option}" from dropdown "{dropdown_name}" with identifier "{identifier}"')
@step('selecciono la opción "{option}" del dropdown "{dropdown_name}" con identificador "{identifier}"')
@step('que selecciono la opción "{option}" del dropdown "{dropdown_name}" con identificador "{identifier}"')
def step_select_option(context, option, dropdown_name, identifier):
    """Selecciona una opción de un dropdown"""
    locator = context.element_locator.get_locator(identifier)
    resolved_option = context.variable_manager.resolve_variables(option)
    context.page.select_option(locator, resolved_option)

@step('I check the checkbox "{checkbox_name}" with identifier "{identifier}"')
@step('marco el checkbox "{checkbox_name}" con identificador "{identifier}"')
@step('que marco el checkbox "{checkbox_name}" con identificador "{identifier}"')
def step_check_checkbox(context, checkbox_name, identifier):
    """Marca un checkbox"""
    locator = context.element_locator.get_locator(identifier)
    context.page.check(locator)

@step('I uncheck the checkbox "{checkbox_name}" with identifier "{identifier}"')
@step('desmarco el checkbox "{checkbox_name}" con identificador "{identifier}"')
@step('que desmarco el checkbox "{checkbox_name}" con identificador "{identifier}"')
def step_uncheck_checkbox(context, checkbox_name, identifier):
    """Desmarca un checkbox"""
    locator = context.element_locator.get_locator(identifier)
    context.page.uncheck(locator)

@step('I press the key "{key}"')
@step('presiono la tecla "{key}"')
@step('que presiono la tecla "{key}"')
def step_press_key(context, key):
    """Presiona una tecla"""
    context.page.keyboard.press(key)

@step('I upload the file "{file_path}" to "{field_name}" with identifier "{identifier}"')
@step('subo el archivo "{file_path}" al campo "{field_name}" con identificador "{identifier}"')
@step('que subo el archivo "{file_path}" al campo "{field_name}" con identificador "{identifier}"')
def step_upload_file(context, file_path, field_name, identifier):
    """Sube un archivo"""
    locator = context.element_locator.get_locator(identifier)
    resolved_path = context.variable_manager.resolve_variables(file_path)
    context.page.set_input_files(locator, resolved_path)