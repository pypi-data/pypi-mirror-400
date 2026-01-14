from behave import step
from playwright.sync_api import TimeoutError

@step('I wait for the element "{element_name}" to be visible with identifier "{identifier}"')
@step('espero a que el elemento "{element_name}" sea visible con identificador "{identifier}"')
@step('que espero a que el elemento "{element_name}" sea visible con identificador "{identifier}"')
def step_wait_element_visible(context, element_name, identifier):
    """Espera a que un elemento sea visible"""
    locator = context.element_locator.get_locator(identifier)
    context.page.wait_for_selector(locator, state='visible')

@step('I wait for the element "{element_name}" to be hidden with identifier "{identifier}"')
@step('espero a que el elemento "{element_name}" esté oculto con identificador "{identifier}"')
@step('que espero a que el elemento "{element_name}" esté oculto con identificador "{identifier}"')
def step_wait_element_hidden(context, element_name, identifier):
    """Espera a que un elemento esté oculto"""
    locator = context.element_locator.get_locator(identifier)
    context.page.wait_for_selector(locator, state='hidden')

@step('I wait for the element "{element_name}" to be enabled with identifier "{identifier}"')
@step('espero a que el elemento "{element_name}" esté habilitado con identificador "{identifier}"')
@step('que espero a que el elemento "{element_name}" esté habilitado con identificador "{identifier}"')
def step_wait_element_enabled(context, element_name, identifier):
    """Espera a que un elemento esté habilitado"""
    locator = context.element_locator.get_locator(identifier)
    context.page.locator(locator).wait_for(state='attached')
    context.page.wait_for_function(f"document.querySelector('{locator}') && !document.querySelector('{locator}').disabled")

@step('I wait for the element "{element_name}" to contain text "{text}" with identifier "{identifier}"')
@step('espero a que el elemento "{element_name}" contenga el texto "{text}" con identificador "{identifier}"')
@step('que espero a que el elemento "{element_name}" contenga el texto "{text}" con identificador "{identifier}"')
def step_wait_element_contains_text(context, element_name, text, identifier):
    """Espera a que un elemento contenga un texto específico"""
    locator = context.element_locator.get_locator(identifier)
    resolved_text = context.variable_manager.resolve_variables(text)
    context.page.locator(locator).wait_for(state='attached')
    context.page.wait_for_function(
        f"document.querySelector('{locator}') && document.querySelector('{locator}').textContent.includes('{resolved_text}')"
    )

@step('I wait for the page url to contain "{url_part}"')
@step('espero a que la url de la página contenga "{url_part}"')
@step('que espero a que la url de la página contenga "{url_part}"')
def step_wait_url_contains(context, url_part):
    """Espera a que la URL contenga una parte específica"""
    resolved_url_part = context.variable_manager.resolve_variables(url_part)
    context.page.wait_for_url(f"**/*{resolved_url_part}*")

@step('I wait for the page title to be "{title}"')
@step('espero a que el título de la página sea "{title}"')
@step('que espero a que el título de la página sea "{title}"')
def step_wait_page_title(context, title):
    """Espera a que el título de la página sea específico"""
    resolved_title = context.variable_manager.resolve_variables(title)
    context.page.wait_for_function(f"document.title === '{resolved_title}'")

@step('I wait for network to be idle')
@step('espero a que la red esté inactiva')
@step('que espero a que la red esté inactiva')
def step_wait_network_idle(context):
    """Espera a que la red esté inactiva"""
    context.page.wait_for_load_state('networkidle')

@step('I wait for dom content to be loaded')
@step('espero a que el contenido del DOM esté cargado')
@step('que espero a que el contenido del DOM esté cargado')
def step_wait_dom_content_loaded(context):
    """Espera a que el contenido del DOM esté cargado"""
    context.page.wait_for_load_state('domcontentloaded')

@step('I wait for the element "{element_name}" to be clickable with identifier "{identifier}"')
@step('espero a que el elemento "{element_name}" sea clickeable con identificador "{identifier}"')
@step('que espero a que el elemento "{element_name}" sea clickeable con identificador "{identifier}"')
def step_wait_element_clickable(context, element_name, identifier):
    """Espera a que un elemento sea clickeable"""
    locator = context.element_locator.get_locator(identifier)
    element = context.page.locator(locator)
    element.wait_for(state='visible')
    element.wait_for(state='attached')
    context.page.wait_for_function(
        f"document.querySelector('{locator}') && !document.querySelector('{locator}').disabled"
    )