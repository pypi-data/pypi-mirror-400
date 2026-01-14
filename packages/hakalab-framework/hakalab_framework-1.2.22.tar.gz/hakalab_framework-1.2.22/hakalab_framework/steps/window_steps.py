import os
from behave import step

@step('I switch to the new window')
@step('cambio a la nueva ventana')
@step('que cambio a la nueva ventana')
def step_switch_to_new_window(context):
    """Cambia a la ventana más reciente"""
    pages = context.browser.pages
    if len(pages) > 1:
        context.page = pages[-1]  # La última ventana abierta
    else:
        raise Exception("No hay ventanas adicionales disponibles")

@step('I close the current window')
@step('cierro la ventana actual')
@step('que cierro la ventana actual')
def step_close_current_window(context):
    """Cierra la ventana actual"""
    context.page.close()
    # Cambiar a la primera ventana disponible si existe
    pages = context.browser.pages
    if pages:
        context.page = pages[0]

@step('I switch to window with title "{title}"')
@step('cambio a la ventana con título "{title}"')
@step('que cambio a la ventana con título "{title}"')
def step_switch_to_window_by_title(context, title):
    """Cambia a una ventana específica por su título"""
    resolved_title = context.variable_manager.resolve_variables(title)
    pages = context.browser.pages
    for page in pages:
        if page.title() == resolved_title:
            context.page = page
            return
    raise Exception(f"No se encontró ventana con título: {resolved_title}")

@step('I switch to window with url containing "{url_part}"')
@step('cambio a la ventana con url que contiene "{url_part}"')
@step('que cambio a la ventana con url que contiene "{url_part}"')
def step_switch_to_window_by_url(context, url_part):
    """Cambia a una ventana específica por parte de su URL"""
    resolved_url_part = context.variable_manager.resolve_variables(url_part)
    pages = context.browser.pages
    for page in pages:
        if resolved_url_part in page.url:
            context.page = page
            return
    raise Exception(f"No se encontró ventana con URL que contenga: {resolved_url_part}")

@step('I accept the alert')
@step('acepto la alerta')
@step('que acepto la alerta')
def step_accept_alert(context):
    """Acepta una alerta de JavaScript"""
    context.page.on("dialog", lambda dialog: dialog.accept())

@step('I dismiss the alert')
@step('rechazo la alerta')
@step('que rechazo la alerta')
def step_dismiss_alert(context):
    """Rechaza una alerta de JavaScript"""
    context.page.on("dialog", lambda dialog: dialog.dismiss())

@step('I accept the alert with text "{text}"')
@step('acepto la alerta con texto "{text}"')
@step('que acepto la alerta con texto "{text}"')
def step_accept_alert_with_text(context, text):
    """Acepta una alerta y envía texto"""
    resolved_text = context.variable_manager.resolve_variables(text)
    context.page.on("dialog", lambda dialog: dialog.accept(resolved_text))

@step('I get the alert text and store it in variable "{variable_name}"')
@step('obtengo el texto de la alerta y lo guardo en la variable "{variable_name}"')
@step('que obtengo el texto de la alerta y lo guardo en la variable "{variable_name}"')
def step_get_alert_text(context, variable_name):
    """Obtiene el texto de una alerta y lo guarda en una variable"""
    def handle_dialog(dialog):
        context.variable_manager.set_variable(variable_name, dialog.message)
        dialog.accept()
    
    context.page.on("dialog", handle_dialog)

@step('I switch to frame "{frame_name}" with identifier "{identifier}"')
@step('cambio al frame "{frame_name}" con identificador "{identifier}"')
@step('que cambio al frame "{frame_name}" con identificador "{identifier}"')
def step_switch_to_frame(context, frame_name, identifier):
    """Cambia a un frame específico"""
    locator = context.element_locator.get_locator(identifier)
    frame_element = context.page.locator(locator)
    context.current_frame = frame_element.content_frame()

@step('I switch to the main content')
@step('cambio al contenido principal')
@step('que cambio al contenido principal')
def step_switch_to_main_content(context):
    """Cambia de vuelta al contenido principal (fuera de frames)"""
    context.current_frame = None

@step('I take a screenshot and save it as "{filename}"')
@step('tomo una captura de pantalla y la guardo como "{filename}"')
@step('que tomo una captura de pantalla y la guardo como "{filename}"')
def step_take_screenshot(context, filename):
    """Toma una captura de pantalla"""
    resolved_filename = context.variable_manager.resolve_variables(filename)
    
    # Usar configuración de página completa
    full_page = os.getenv('SCREENSHOT_FULL_PAGE', 'true').lower() == 'true'
    context.page.screenshot(path=resolved_filename, full_page=full_page, type='png')

@step('I take a screenshot of element "{element_name}" and save it as "{filename}" with identifier "{identifier}"')
@step('tomo una captura del elemento "{element_name}" y la guardo como "{filename}" con identificador "{identifier}"')
@step('que tomo una captura del elemento "{element_name}" y la guardo como "{filename}" con identificador "{identifier}"')
def step_take_element_screenshot(context, element_name, filename, identifier):
    """Toma una captura de pantalla de un elemento específico"""
    locator = context.element_locator.get_locator(identifier)
    resolved_filename = context.variable_manager.resolve_variables(filename)
    context.page.locator(locator).screenshot(path=resolved_filename)