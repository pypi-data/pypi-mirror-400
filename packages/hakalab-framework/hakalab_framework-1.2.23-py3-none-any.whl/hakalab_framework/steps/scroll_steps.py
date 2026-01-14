from behave import step

@step('I scroll to the element "{element_name}" with identifier "{identifier}"')
@step('hago scroll al elemento "{element_name}" con identificador "{identifier}"')
@step('que hago scroll al elemento "{element_name}" con identificador "{identifier}"')
def step_scroll_to_element(context, element_name, identifier):
    """Hace scroll hasta un elemento específico"""
    locator = context.element_locator.get_locator(identifier)
    context.page.locator(locator).scroll_into_view_if_needed()

@step('I scroll to the top of the page')
@step('hago scroll al inicio de la página')
@step('que hago scroll al inicio de la página')
def step_scroll_to_top(context):
    """Hace scroll al inicio de la página"""
    context.page.evaluate("window.scrollTo(0, 0)")

@step('I scroll to the bottom of the page')
@step('hago scroll al final de la página')
@step('que hago scroll al final de la página')
def step_scroll_to_bottom(context):
    """Hace scroll al final de la página"""
    context.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

@step('I scroll down {pixels:d} pixels')
@step('hago scroll hacia abajo {pixels:d} píxeles')
@step('que hago scroll hacia abajo {pixels:d} píxeles')
def step_scroll_down_pixels(context, pixels):
    """Hace scroll hacia abajo un número específico de píxeles"""
    context.page.evaluate(f"window.scrollBy(0, {pixels})")

@step('I scroll up {pixels:d} pixels')
@step('hago scroll hacia arriba {pixels:d} píxeles')
@step('que hago scroll hacia arriba {pixels:d} píxeles')
def step_scroll_up_pixels(context, pixels):
    """Hace scroll hacia arriba un número específico de píxeles"""
    context.page.evaluate(f"window.scrollBy(0, -{pixels})")

@step('I scroll left {pixels:d} pixels')
@step('hago scroll hacia la izquierda {pixels:d} píxeles')
@step('que hago scroll hacia la izquierda {pixels:d} píxeles')
def step_scroll_left_pixels(context, pixels):
    """Hace scroll hacia la izquierda un número específico de píxeles"""
    context.page.evaluate(f"window.scrollBy(-{pixels}, 0)")

@step('I scroll right {pixels:d} pixels')
@step('hago scroll hacia la derecha {pixels:d} píxeles')
@step('que hago scroll hacia la derecha {pixels:d} píxeles')
def step_scroll_right_pixels(context, pixels):
    """Hace scroll hacia la derecha un número específico de píxeles"""
    context.page.evaluate(f"window.scrollBy({pixels}, 0)")

@step('I scroll the element "{element_name}" down {pixels:d} pixels with identifier "{identifier}"')
@step('hago scroll del elemento "{element_name}" hacia abajo {pixels:d} píxeles con identificador "{identifier}"')
@step('que hago scroll del elemento "{element_name}" hacia abajo {pixels:d} píxeles con identificador "{identifier}"')
def step_scroll_element_down(context, element_name, pixels, identifier):
    """Hace scroll hacia abajo dentro de un elemento específico"""
    locator = context.element_locator.get_locator(identifier)
    context.page.locator(locator).evaluate(f"element => element.scrollBy(0, {pixels})")

@step('I scroll the element "{element_name}" up {pixels:d} pixels with identifier "{identifier}"')
@step('hago scroll del elemento "{element_name}" hacia arriba {pixels:d} píxeles con identificador "{identifier}"')
@step('que hago scroll del elemento "{element_name}" hacia arriba {pixels:d} píxeles con identificador "{identifier}"')
def step_scroll_element_up(context, element_name, pixels, identifier):
    """Hace scroll hacia arriba dentro de un elemento específico"""
    locator = context.element_locator.get_locator(identifier)
    context.page.locator(locator).evaluate(f"element => element.scrollBy(0, -{pixels})")