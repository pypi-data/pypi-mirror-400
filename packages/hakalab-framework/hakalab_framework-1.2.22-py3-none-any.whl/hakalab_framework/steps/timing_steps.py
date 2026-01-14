#!/usr/bin/env python3
"""
Steps para manejo de tiempos, esperas y delays
Permite controlar el timing de la ejecución de pruebas
"""
import time
from datetime import datetime, timedelta
from behave import step

@step('pauso {seconds:d} segundos')
def step_pause_seconds(context, seconds):
    """Pausa un número específico de segundos (alternativa a espero)"""
    print(f"⏸️ Pausando {seconds} segundos...")
    time.sleep(seconds)
    print(f"✅ Pausa completada ({seconds}s)")

@step('espero {milliseconds:d} milisegundos')
@step('que espero {milliseconds:d} milisegundos')
@step('pauso {milliseconds:d} milisegundos')
def step_wait_milliseconds(context, milliseconds):
    """Espera un número específico de milisegundos"""
    seconds = milliseconds / 1000
    print(f"⏰ Esperando {milliseconds} milisegundos...")
    time.sleep(seconds)
    print(f"✅ Espera completada ({milliseconds}ms)")

@step('espero aleatoriamente entre {min_seconds:d} y {max_seconds:d} segundos')
@step('que espero tiempo aleatorio entre {min_seconds:d} y {max_seconds:d} segundos')
def step_wait_random_seconds(context, min_seconds, max_seconds):
    """Espera un tiempo aleatorio entre dos valores"""
    import random
    wait_time = random.randint(min_seconds, max_seconds)
    print(f"⏰ Esperando {wait_time} segundos (aleatorio entre {min_seconds}-{max_seconds})...")
    time.sleep(wait_time)
    print(f"✅ Espera aleatoria completada ({wait_time}s)")

@step('espero hasta que el elemento "{selector}" sea visible')
@step('que espero a que "{selector}" aparezca')
def step_wait_for_element_visible(context, selector):
    """Espera hasta que un elemento sea visible"""
    print(f"⏰ Esperando a que el elemento '{selector}' sea visible...")
    
    # Obtener elemento
    if hasattr(context, 'get_element'):
        element = context.get_element(selector)
    else:
        element = context.page.locator(selector)
    
    # Esperar a que sea visible
    element.wait_for(state='visible')
    print(f"✅ Elemento '{selector}' ahora es visible")

@step('espero hasta que el elemento "{selector}" desaparezca')
@step('que espero a que "{selector}" desaparezca')
def step_wait_for_element_hidden(context, selector):
    """Espera hasta que un elemento desaparezca"""
    print(f"⏰ Esperando a que el elemento '{selector}' desaparezca...")
    
    # Obtener elemento
    if hasattr(context, 'get_element'):
        element = context.get_element(selector)
    else:
        element = context.page.locator(selector)
    
    # Esperar a que esté oculto
    element.wait_for(state='hidden')
    print(f"✅ Elemento '{selector}' ahora está oculto")

@step('espero hasta que el elemento "{selector}" esté habilitado')
@step('que espero a que "{selector}" se habilite')
def step_wait_for_element_enabled(context, selector):
    """Espera hasta que un elemento esté habilitado"""
    print(f"⏰ Esperando a que el elemento '{selector}' esté habilitado...")
    
    # Obtener elemento
    if hasattr(context, 'get_element'):
        element = context.get_element(selector)
    else:
        element = context.page.locator(selector)
    
    # Esperar a que esté habilitado
    element.wait_for(state='visible')
    context.page.wait_for_function(
        f"document.querySelector('{selector}') && !document.querySelector('{selector}').disabled"
    )
    print(f"✅ Elemento '{selector}' ahora está habilitado")

@step('espero hasta que el elemento "{selector}" contenga el texto "{expected_text}"')
@step('que espero a que "{selector}" contenga "{expected_text}"')
def step_wait_for_element_text(context, selector, expected_text):
    """Espera hasta que un elemento contenga un texto específico"""
    print(f"⏰ Esperando a que '{selector}' contenga '{expected_text}'...")
    
    # Resolver variables en el texto esperado
    if hasattr(context, 'variable_manager'):
        expected_text = context.variable_manager.resolve_variables(expected_text)
    
    # Obtener elemento
    if hasattr(context, 'get_element'):
        element = context.get_element(selector)
    else:
        element = context.page.locator(selector)
    
    # Esperar hasta que contenga el texto
    element.wait_for(state='visible')
    
    # Polling para verificar el texto
    max_attempts = 30  # 30 segundos máximo
    for attempt in range(max_attempts):
        try:
            current_text = element.text_content()
            if expected_text in current_text:
                print(f"✅ Elemento '{selector}' ahora contiene '{expected_text}'")
                return
        except:
            pass
        time.sleep(1)
    
    raise TimeoutError(f"El elemento '{selector}' no contuvo '{expected_text}' después de {max_attempts} segundos")

@step('espero hasta que la página termine de cargar')
@step('que espero a que la página cargue completamente')
def step_wait_for_page_load(context):
    """Espera hasta que la página termine de cargar completamente"""
    print("⏰ Esperando a que la página termine de cargar...")
    
    # Esperar a que el estado de la página sea 'load'
    context.page.wait_for_load_state('load')
    
    # Esperar adicional para JavaScript
    context.page.wait_for_load_state('networkidle')
    
    print("✅ Página cargada completamente")

@step('espero hasta que no haya requests de red pendientes')
@step('que espero a que termine la actividad de red')
def step_wait_for_network_idle(context):
    """Espera hasta que no haya actividad de red"""
    print("⏰ Esperando a que termine la actividad de red...")
    context.page.wait_for_load_state('networkidle')
    print("✅ Actividad de red completada")

@step('espero con timeout de {timeout:d} segundos hasta que "{selector}" sea visible')
@step('que espero máximo {timeout:d} segundos a que "{selector}" aparezca')
def step_wait_for_element_with_timeout(context, timeout, selector):
    """Espera un elemento con timeout personalizado"""
    print(f"⏰ Esperando hasta {timeout}s a que '{selector}' sea visible...")
    
    # Obtener elemento
    if hasattr(context, 'get_element'):
        element = context.get_element(selector)
    else:
        element = context.page.locator(selector)
    
    # Esperar con timeout personalizado
    try:
        element.wait_for(state='visible', timeout=timeout * 1000)
        print(f"✅ Elemento '{selector}' visible dentro del timeout ({timeout}s)")
    except Exception as e:
        raise TimeoutError(f"Elemento '{selector}' no apareció en {timeout} segundos: {e}")

@step('establezco el timeout global en {timeout:d} segundos')
@step('que configuro timeout de {timeout:d} segundos')
def step_set_global_timeout(context, timeout):
    """Establece el timeout global para las operaciones"""
    context.page.set_default_timeout(timeout * 1000)
    print(f"✅ Timeout global establecido en {timeout} segundos")

@step('espero hasta que el elemento "{selector}" tenga el atributo "{attribute}" con valor "{expected_value}"')
def step_wait_for_element_attribute(context, selector, attribute, expected_value):
    """Espera hasta que un elemento tenga un atributo con valor específico"""
    print(f"⏰ Esperando a que '{selector}' tenga {attribute}='{expected_value}'...")
    
    # Resolver variables
    if hasattr(context, 'variable_manager'):
        expected_value = context.variable_manager.resolve_variables(expected_value)
    
    # Obtener elemento
    if hasattr(context, 'get_element'):
        element = context.get_element(selector)
    else:
        element = context.page.locator(selector)
    
    # Polling para verificar el atributo
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            current_value = element.get_attribute(attribute)
            if current_value == expected_value:
                print(f"✅ Elemento '{selector}' ahora tiene {attribute}='{expected_value}'")
                return
        except:
            pass
        time.sleep(1)
    
    raise TimeoutError(f"El elemento '{selector}' no tuvo {attribute}='{expected_value}' después de {max_attempts} segundos")

@step('espero hasta que haya {count:d} elementos "{selector}"')
@step('que espero a que existan {count:d} elementos "{selector}"')
def step_wait_for_element_count(context, count, selector):
    """Espera hasta que haya un número específico de elementos"""
    print(f"⏰ Esperando a que haya {count} elementos '{selector}'...")
    
    # Obtener localizador
    if hasattr(context, 'get_element'):
        # Si tenemos get_element, obtener el localizador base
        locator_str = selector
        if hasattr(context, 'element_locator'):
            locator_str = context.element_locator.get_locator(selector)
        elements = context.page.locator(locator_str)
    else:
        elements = context.page.locator(selector)
    
    # Esperar hasta que haya el número correcto de elementos
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            current_count = elements.count()
            if current_count == count:
                print(f"✅ Ahora hay {count} elementos '{selector}'")
                return
        except:
            pass
        time.sleep(1)
    
    current_count = elements.count()
    raise TimeoutError(f"Se esperaban {count} elementos '{selector}', pero hay {current_count} después de 30 segundos")

@step('espero hasta que la URL contenga "{url_part}"')
@step('que espero a que la URL contenga "{url_part}"')
def step_wait_for_url_contains(context, url_part):
    """Espera hasta que la URL contenga una parte específica"""
    print(f"⏰ Esperando a que la URL contenga '{url_part}'...")
    
    # Resolver variables
    if hasattr(context, 'variable_manager'):
        url_part = context.variable_manager.resolve_variables(url_part)
    
    # Esperar hasta que la URL contenga la parte especificada
    context.page.wait_for_url(f"**/*{url_part}*")
    print(f"✅ URL ahora contiene '{url_part}'")

@step('marco el tiempo de inicio como "{timer_name}"')
@step('que inicio el cronómetro "{timer_name}"')
def step_start_timer(context, timer_name):
    """Inicia un cronómetro con nombre específico"""
    if not hasattr(context, 'timers'):
        context.timers = {}
    
    context.timers[timer_name] = datetime.now()
    print(f"⏱️ Cronómetro '{timer_name}' iniciado")

@step('verifico que el cronómetro "{timer_name}" no exceda {max_seconds:d} segundos')
@step('que el tiempo del cronómetro "{timer_name}" sea menor a {max_seconds:d} segundos')
def step_verify_timer_duration(context, timer_name, max_seconds):
    """Verifica que un cronómetro no exceda un tiempo máximo"""
    if not hasattr(context, 'timers') or timer_name not in context.timers:
        raise ValueError(f"Cronómetro '{timer_name}' no fue iniciado")
    
    start_time = context.timers[timer_name]
    current_time = datetime.now()
    elapsed = (current_time - start_time).total_seconds()
    
    assert elapsed <= max_seconds, f"Cronómetro '{timer_name}' excedió {max_seconds}s (actual: {elapsed:.2f}s)"
    print(f"✅ Cronómetro '{timer_name}': {elapsed:.2f}s (límite: {max_seconds}s)")

@step('muestro el tiempo transcurrido del cronómetro "{timer_name}"')
@step('que imprimo el tiempo del cronómetro "{timer_name}"')
def step_show_timer_duration(context, timer_name):
    """Muestra el tiempo transcurrido de un cronómetro"""
    if not hasattr(context, 'timers') or timer_name not in context.timers:
        print(f"❌ Cronómetro '{timer_name}' no fue iniciado")
        return
    
    start_time = context.timers[timer_name]
    current_time = datetime.now()
    elapsed = (current_time - start_time).total_seconds()
    
    print(f"⏱️ Cronómetro '{timer_name}': {elapsed:.2f} segundos transcurridos")

# Steps adicionales para casos específicos
@step('espero hasta que el elemento "{selector}" no esté en estado de carga')
@step('que espero a que "{selector}" termine de cargar')
def step_wait_for_element_not_loading(context, selector):
    """Espera hasta que un elemento no esté en estado de carga"""
    print(f"⏰ Esperando a que '{selector}' termine de cargar...")
    
    # Obtener elemento
    if hasattr(context, 'get_element'):
        element = context.get_element(selector)
    else:
        element = context.page.locator(selector)
    
    # Esperar hasta que no tenga clases de loading comunes
    max_attempts = 30
    loading_classes = ['loading', 'spinner', 'busy', 'processing']
    
    for attempt in range(max_attempts):
        try:
            class_list = element.get_attribute('class') or ""
            has_loading_class = any(loading_class in class_list.lower() for loading_class in loading_classes)
            
            if not has_loading_class:
                print(f"✅ Elemento '{selector}' terminó de cargar")
                return
        except:
            pass
        time.sleep(1)
    
    print(f"⚠️ Elemento '{selector}' puede seguir cargando después de 30 segundos")

@step('espero progresivamente: {wait_pattern}')
@step('que espero con patrón: {wait_pattern}')
def step_progressive_wait(context, wait_pattern):
    """Espera con patrón progresivo (ej: "1,2,3,5" segundos)"""
    try:
        wait_times = [int(x.strip()) for x in wait_pattern.split(',')]
        
        print(f"⏰ Iniciando espera progresiva: {wait_times} segundos...")
        
        for i, wait_time in enumerate(wait_times, 1):
            print(f"   Paso {i}/{len(wait_times)}: esperando {wait_time}s...")
            time.sleep(wait_time)
        
        total_time = sum(wait_times)
        print(f"✅ Espera progresiva completada (total: {total_time}s)")
        
    except ValueError:
        raise ValueError(f"Patrón de espera inválido: '{wait_pattern}'. Use formato: '1,2,3,5'")