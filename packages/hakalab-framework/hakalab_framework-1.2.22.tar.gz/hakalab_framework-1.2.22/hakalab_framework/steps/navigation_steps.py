from behave import step
import time

@step('I go to the url "{url}"')
@step('I navigate to "{url}"')
@step('voy a la url "{url}"')
@step('que voy a la url "{url}"')
def step_navigate_to_url(context, url):
    """Navega a una URL específica y espera a que la página cargue completamente"""
    resolved_url = context.variable_manager.resolve_variables(url)
    
    try:
        # Navegar con opciones de espera robustas
        context.page.goto(
            resolved_url,
            wait_until="networkidle",  # Esperar hasta que no haya requests por 500ms
            timeout=30000  # Timeout de 30 segundos
        )
        
        # Esperar adicional para asegurar que la página esté completamente cargada
        context.page.wait_for_load_state("domcontentloaded")
        context.page.wait_for_load_state("networkidle")
        
        # Log de éxito
        if hasattr(context, 'logger'):
            context.logger.info(f"Navegación exitosa a: {resolved_url}")
        
    except Exception as e:
        # Log del error
        if hasattr(context, 'logger'):
            context.logger.error(f"Error navegando a {resolved_url}: {e}")
        
        # Intentar navegación básica como fallback
        try:
            context.page.goto(resolved_url, timeout=15000)
            context.page.wait_for_load_state("domcontentloaded")
            if hasattr(context, 'logger'):
                context.logger.warning(f"Navegación con fallback exitosa a: {resolved_url}")
        except Exception as fallback_error:
            if hasattr(context, 'logger'):
                context.logger.error(f"Error en fallback: {fallback_error}")
            raise Exception(f"No se pudo navegar a {resolved_url}: {fallback_error}")

@step('I go back')
@step('voy hacia atrás')
@step('que voy hacia atrás')
def step_go_back(context):
    """Navega hacia atrás en el historial y espera a que cargue"""
    try:
        context.page.go_back(wait_until="networkidle", timeout=15000)
        context.page.wait_for_load_state("domcontentloaded")
        
        if hasattr(context, 'logger'):
            context.logger.info("Navegación hacia atrás exitosa")
    except Exception as e:
        if hasattr(context, 'logger'):
            context.logger.error(f"Error navegando hacia atrás: {e}")
        raise

@step('I go forward')
@step('voy hacia adelante')
@step('que voy hacia adelante')
def step_go_forward(context):
    """Navega hacia adelante en el historial y espera a que cargue"""
    try:
        context.page.go_forward(wait_until="networkidle", timeout=15000)
        context.page.wait_for_load_state("domcontentloaded")
        
        if hasattr(context, 'logger'):
            context.logger.info("Navegación hacia adelante exitosa")
    except Exception as e:
        if hasattr(context, 'logger'):
            context.logger.error(f"Error navegando hacia adelante: {e}")
        raise

@step('I reload the page')
@step('recargo la página')
@step('que recargo la página')
def step_reload_page(context):
    """Recarga la página actual y espera a que cargue completamente"""
    try:
        context.page.reload(wait_until="networkidle", timeout=30000)
        context.page.wait_for_load_state("domcontentloaded")
        
        if hasattr(context, 'logger'):
            context.logger.info("Recarga de página exitosa")
    except Exception as e:
        if hasattr(context, 'logger'):
            context.logger.error(f"Error recargando página: {e}")
        raise

@step('I wait for {seconds:d} seconds')
@step('espero {seconds:d} segundos')
@step('que espero {seconds:d} segundos')
def step_wait_seconds(context, seconds):
    """Espera un número específico de segundos"""
    time.sleep(seconds)

@step('I wait for the page to load')
@step('espero a que cargue la página')
@step('que espero a que cargue la página')
def step_wait_page_load(context):
    """Espera a que la página termine de cargar"""
    context.page.wait_for_load_state('networkidle')

@step('I open a new tab')
@step('abro una nueva pestaña')
@step('que abro una nueva pestaña')
def step_open_new_tab(context):
    """Abre una nueva pestaña"""
    context.page = context.browser.new_page()
    context.page.set_default_timeout(context.timeout)

@step('I close the current tab')
@step('cierro la pestaña actual')
@step('que cierro la pestaña actual')
def step_close_current_tab(context):
    """Cierra la pestaña actual"""
    context.page.close()

@step('I switch to tab {tab_index:d}')
@step('cambio a la pestaña {tab_index:d}')
@step('que cambio a la pestaña {tab_index:d}')
def step_switch_to_tab(context, tab_index):
    """Cambia a una pestaña específica por índice"""
    pages = context.browser.pages
    if 0 <= tab_index < len(pages):
        context.page = pages[tab_index]
    else:
        raise IndexError(f"Índice de pestaña {tab_index} fuera de rango. Pestañas disponibles: {len(pages)}")

@step('I maximize the window')
@step('maximizo la ventana')
@step('que maximizo la ventana')
def step_maximize_window(context):
    """Maximiza la ventana del navegador"""
    context.page.set_viewport_size({"width": 1920, "height": 1080})

@step('I set window size to {width:d}x{height:d}')
@step('establezco el tamaño de ventana a {width:d}x{height:d}')
@step('que establezco el tamaño de ventana a {width:d}x{height:d}')
def step_set_window_size(context, width, height):
    """Establece el tamaño de la ventana"""
    context.page.set_viewport_size({"width": width, "height": height})