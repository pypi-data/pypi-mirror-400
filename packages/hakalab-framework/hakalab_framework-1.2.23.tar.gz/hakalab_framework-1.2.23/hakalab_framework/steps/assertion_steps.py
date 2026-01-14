from behave import step
from playwright.sync_api import expect

@step('I should see text "{text}"')
@step('debería ver el texto "{text}"')
@step('que debería ver el texto "{text}"')
def step_should_see_text(context, text):
    """Verifica que un texto sea visible en la página"""
    resolved_text = context.variable_manager.resolve_variables(text)
    expect(context.page.locator(f'text="{resolved_text}"')).to_be_visible()

@step('I should not see text "{text}"')
@step('no debería ver el texto "{text}"')
@step('que no debería ver el texto "{text}"')
def step_should_not_see_text(context, text):
    """Verifica que un texto no sea visible en la página"""
    resolved_text = context.variable_manager.resolve_variables(text)
    expect(context.page.locator(f'text="{resolved_text}"')).not_to_be_visible()

@step('the page title should be "{title}"')
@step('el título de la página debería ser "{title}"')
@step('que el título de la página debería ser "{title}"')
def step_page_title_should_be(context, title):
    """Verifica que el título de la página sea exacto"""
    resolved_title = context.variable_manager.resolve_variables(title)
    expect(context.page).to_have_title(resolved_title)

@step('the page title should contain "{text}"')
@step('el título de la página debería contener "{text}"')
@step('que el título de la página debería contener "{text}"')
def step_page_title_should_contain(context, text):
    """Verifica que el título de la página contenga un texto"""
    resolved_text = context.variable_manager.resolve_variables(text)
    expect(context.page).to_have_title(f".*{resolved_text}.*")

@step('I should see the element "{element_name}" with identifier "{identifier}"')
@step('debería ver el elemento "{element_name}" con identificador "{identifier}"')
@step('que debería ver el elemento "{element_name}" con identificador "{identifier}"')
def step_should_see_element(context, element_name, identifier):
    """Verifica que un elemento sea visible"""
    locator = context.element_locator.get_locator(identifier)
    expect(context.page.locator(locator)).to_be_visible()

@step('I should not see the element "{element_name}" with identifier "{identifier}"')
@step('no debería ver el elemento "{element_name}" con identificador "{identifier}"')
@step('que no debería ver el elemento "{element_name}" con identificador "{identifier}"')
def step_should_not_see_element(context, element_name, identifier):
    """Verifica que un elemento no sea visible"""
    locator = context.element_locator.get_locator(identifier)
    expect(context.page.locator(locator)).not_to_be_visible()

@step('the element "{element_name}" should contain the text "{text}" with identifier "{identifier}"')
@step('el elemento "{element_name}" debería contener el texto "{text}" con identificador "{identifier}"')
@step('que el elemento "{element_name}" debería contener el texto "{text}" con identificador "{identifier}"')
def step_element_should_contain_text(context, element_name, text, identifier):
    """Verifica que un elemento contenga un texto específico"""
    locator = context.element_locator.get_locator(identifier)
    resolved_text = context.variable_manager.resolve_variables(text)
    expect(context.page.locator(locator)).to_contain_text(resolved_text)

@step('the element "{element_name}" should have the exact text "{text}" with identifier "{identifier}"')
@step('el elemento "{element_name}" debería tener el texto exacto "{text}" con identificador "{identifier}"')
@step('que el elemento "{element_name}" debería tener el texto exacto "{text}" con identificador "{identifier}"')
def step_element_should_have_text(context, element_name, text, identifier):
    """Verifica que un elemento tenga un texto exacto"""
    locator = context.element_locator.get_locator(identifier)
    resolved_text = context.variable_manager.resolve_variables(text)
    expect(context.page.locator(locator)).to_have_text(resolved_text)

@step('the field "{field_name}" should have the value "{value}" with identifier "{identifier}"')
@step('el campo "{field_name}" debería tener el valor "{value}" con identificador "{identifier}"')
@step('que el campo "{field_name}" debería tener el valor "{value}" con identificador "{identifier}"')
def step_field_should_have_value(context, field_name, value, identifier):
    """Verifica que un campo tenga un valor específico"""
    locator = context.element_locator.get_locator(identifier)
    resolved_value = context.variable_manager.resolve_variables(value)
    expect(context.page.locator(locator)).to_have_value(resolved_value)

@step('the element "{element_name}" should be enabled with identifier "{identifier}"')
@step('el elemento "{element_name}" debería estar habilitado con identificador "{identifier}"')
@step('que el elemento "{element_name}" debería estar habilitado con identificador "{identifier}"')
def step_element_should_be_enabled(context, element_name, identifier):
    """Verifica que un elemento esté habilitado"""
    locator = context.element_locator.get_locator(identifier)
    expect(context.page.locator(locator)).to_be_enabled()

@step('the element "{element_name}" should be disabled with identifier "{identifier}"')
@step('el elemento "{element_name}" debería estar deshabilitado con identificador "{identifier}"')
@step('que el elemento "{element_name}" debería estar deshabilitado con identificador "{identifier}"')
def step_element_should_be_disabled(context, element_name, identifier):
    """Verifica que un elemento esté deshabilitado"""
    locator = context.element_locator.get_locator(identifier)
    expect(context.page.locator(locator)).to_be_disabled()

@step('the checkbox "{checkbox_name}" should be checked with identifier "{identifier}"')
@step('el checkbox "{checkbox_name}" debería estar marcado con identificador "{identifier}"')
@step('que el checkbox "{checkbox_name}" debería estar marcado con identificador "{identifier}"')
def step_checkbox_should_be_checked(context, checkbox_name, identifier):
    """Verifica que un checkbox esté marcado"""
    locator = context.element_locator.get_locator(identifier)
    expect(context.page.locator(locator)).to_be_checked()

@step('the checkbox "{checkbox_name}" should not be checked with identifier "{identifier}"')
@step('el checkbox "{checkbox_name}" no debería estar marcado con identificador "{identifier}"')
@step('que el checkbox "{checkbox_name}" no debería estar marcado con identificador "{identifier}"')
def step_checkbox_should_not_be_checked(context, checkbox_name, identifier):
    """Verifica que un checkbox no esté marcado"""
    locator = context.element_locator.get_locator(identifier)
    expect(context.page.locator(locator)).not_to_be_checked()

@step('the current url should be "{url}"')
@step('la url actual debería ser "{url}"')
@step('que la url actual debería ser "{url}"')
def step_current_url_should_be(context, url):
    """Verifica la URL actual"""
    resolved_url = context.variable_manager.resolve_variables(url)
    expect(context.page).to_have_url(resolved_url)

@step('the current url should contain "{url_part}"')
@step('la url actual debería contener "{url_part}"')
@step('que la url actual debería contener "{url_part}"')
def step_current_url_should_contain(context, url_part):
    """Verifica que la URL actual contenga una parte específica"""
    resolved_url_part = context.variable_manager.resolve_variables(url_part)
    current_url = context.page.url
    assert resolved_url_part in current_url, f"La URL actual '{current_url}' no es correcta"