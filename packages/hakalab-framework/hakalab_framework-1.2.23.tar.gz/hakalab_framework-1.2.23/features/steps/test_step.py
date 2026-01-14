from behave import step

@step('I test navigation to "{url}"')
def test_navigation(context, url):
    """Step de prueba para navegación"""
    print(f"Navegando a: {url}")
    context.page.goto(url)
    print("Navegación completada")