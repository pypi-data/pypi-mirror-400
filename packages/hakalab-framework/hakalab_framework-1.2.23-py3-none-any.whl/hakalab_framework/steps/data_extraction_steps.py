from behave import step

@step('I get the text from element "{element_name}" and store it in variable "{variable_name}" with identifier "{identifier}"')
@step('obtengo el texto del elemento "{element_name}" y lo guardo en la variable "{variable_name}" con identificador "{identifier}"')
@step('que obtengo el texto del elemento "{element_name}" y lo guardo en la variable "{variable_name}" con identificador "{identifier}"')
def step_get_text_and_store(context, element_name, variable_name, identifier):
    """Obtiene el texto de un elemento y lo guarda en una variable"""
    locator = context.element_locator.get_locator(identifier)
    text = context.page.locator(locator).text_content()
    context.variable_manager.set_variable(variable_name, text)

@step('I get the value from field "{field_name}" and store it in variable "{variable_name}" with identifier "{identifier}"')
@step('obtengo el valor del campo "{field_name}" y lo guardo en la variable "{variable_name}" con identificador "{identifier}"')
@step('que obtengo el valor del campo "{field_name}" y lo guardo en la variable "{variable_name}" con identificador "{identifier}"')
def step_get_value_and_store(context, field_name, variable_name, identifier):
    """Obtiene el valor de un campo y lo guarda en una variable"""
    locator = context.element_locator.get_locator(identifier)
    value = context.page.locator(locator).input_value()
    context.variable_manager.set_variable(variable_name, value)

@step('I get the attribute "{attribute}" from element "{element_name}" and store it in variable "{variable_name}" with identifier "{identifier}"')
@step('obtengo el atributo "{attribute}" del elemento "{element_name}" y lo guardo en la variable "{variable_name}" con identificador "{identifier}"')
@step('que obtengo el atributo "{attribute}" del elemento "{element_name}" y lo guardo en la variable "{variable_name}" con identificador "{identifier}"')
def step_get_attribute_and_store(context, attribute, element_name, variable_name, identifier):
    """Obtiene un atributo de un elemento y lo guarda en una variable"""
    locator = context.element_locator.get_locator(identifier)
    attr_value = context.page.locator(locator).get_attribute(attribute)
    context.variable_manager.set_variable(variable_name, attr_value)

@step('I get the css property "{property}" from element "{element_name}" and store it in variable "{variable_name}" with identifier "{identifier}"')
@step('obtengo la propiedad css "{property}" del elemento "{element_name}" y la guardo en la variable "{variable_name}" con identificador "{identifier}"')
@step('que obtengo la propiedad css "{property}" del elemento "{element_name}" y la guardo en la variable "{variable_name}" con identificador "{identifier}"')
def step_get_css_property_and_store(context, property, element_name, variable_name, identifier):
    """Obtiene una propiedad CSS de un elemento y la guarda en una variable"""
    locator = context.element_locator.get_locator(identifier)
    css_value = context.page.locator(locator).evaluate(f"element => getComputedStyle(element).{property}")
    context.variable_manager.set_variable(variable_name, css_value)

@step('I get the current url and store it in variable "{variable_name}"')
@step('obtengo la url actual y la guardo en la variable "{variable_name}"')
@step('que obtengo la url actual y la guardo en la variable "{variable_name}"')
def step_get_current_url_and_store(context, variable_name):
    """Obtiene la URL actual y la guarda en una variable"""
    current_url = context.page.url
    context.variable_manager.set_variable(variable_name, current_url)

@step('I get the page title and store it in variable "{variable_name}"')
@step('obtengo el título de la página y lo guardo en la variable "{variable_name}"')
@step('que obtengo el título de la página y lo guardo en la variable "{variable_name}"')
def step_get_page_title_and_store(context, variable_name):
    """Obtiene el título de la página y lo guarda en una variable"""
    title = context.page.title()
    context.variable_manager.set_variable(variable_name, title)

@step('I count elements with identifier "{identifier}" and store the count in variable "{variable_name}"')
@step('cuento los elementos con identificador "{identifier}" y guardo el conteo en la variable "{variable_name}"')
@step('que cuento los elementos con identificador "{identifier}" y guardo el conteo en la variable "{variable_name}"')
def step_count_elements_and_store(context, identifier, variable_name):
    """Cuenta elementos que coinciden con un localizador y guarda el conteo"""
    locator = context.element_locator.get_locator(identifier)
    count = context.page.locator(locator).count()
    context.variable_manager.set_variable(variable_name, count)

@step('I check if element "{element_name}" is visible and store result in variable "{variable_name}" with identifier "{identifier}"')
@step('verifico si el elemento "{element_name}" es visible y guardo el resultado en la variable "{variable_name}" con identificador "{identifier}"')
@step('que verifico si el elemento "{element_name}" es visible y guardo el resultado en la variable "{variable_name}" con identificador "{identifier}"')
def step_check_element_visibility_and_store(context, element_name, variable_name, identifier):
    """Verifica si un elemento es visible y guarda el resultado"""
    locator = context.element_locator.get_locator(identifier)
    is_visible = context.page.locator(locator).is_visible()
    context.variable_manager.set_variable(variable_name, is_visible)

@step('I check if element "{element_name}" is enabled and store result in variable "{variable_name}" with identifier "{identifier}"')
@step('verifico si el elemento "{element_name}" está habilitado y guardo el resultado en la variable "{variable_name}" con identificador "{identifier}"')
@step('que verifico si el elemento "{element_name}" está habilitado y guardo el resultado en la variable "{variable_name}" con identificador "{identifier}"')
def step_check_element_enabled_and_store(context, element_name, variable_name, identifier):
    """Verifica si un elemento está habilitado y guarda el resultado"""
    locator = context.element_locator.get_locator(identifier)
    is_enabled = context.page.locator(locator).is_enabled()
    context.variable_manager.set_variable(variable_name, is_enabled)

@step('I check if checkbox "{checkbox_name}" is checked and store result in variable "{variable_name}" with identifier "{identifier}"')
@step('verifico si el checkbox "{checkbox_name}" está marcado y guardo el resultado en la variable "{variable_name}" con identificador "{identifier}"')
@step('que verifico si el checkbox "{checkbox_name}" está marcado y guardo el resultado en la variable "{variable_name}" con identificador "{identifier}"')
def step_check_checkbox_state_and_store(context, checkbox_name, variable_name, identifier):
    """Verifica si un checkbox está marcado y guarda el resultado"""
    locator = context.element_locator.get_locator(identifier)
    is_checked = context.page.locator(locator).is_checked()
    context.variable_manager.set_variable(variable_name, is_checked)