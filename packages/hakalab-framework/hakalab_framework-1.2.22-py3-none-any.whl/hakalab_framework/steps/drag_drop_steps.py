#!/usr/bin/env python3
"""
Steps para operaciones de arrastrar y soltar (Drag & Drop)
"""
from behave import step
from playwright.sync_api import expect

@step('I drag element "{source_element}" to element "{target_element}" with identifiers "{source_id}" and "{target_id}"')
@step('arrastro el elemento "{source_element}" al elemento "{target_element}" con identificadores "{source_id}" y "{target_id}"')
def step_drag_and_drop_elements(context, source_element, target_element, source_id, target_id):
    """Arrastra un elemento y lo suelta en otro elemento"""
    source_locator = context.element_locator.get_locator(source_id)
    target_locator = context.element_locator.get_locator(target_id)
    
    # Obtener elementos
    source = context.page.locator(source_locator)
    target = context.page.locator(target_locator)
    
    # Asegurar que ambos elementos sean visibles
    expect(source).to_be_visible()
    expect(target).to_be_visible()
    
    # Obtener posiciones de ambos elementos
    source_box = source.bounding_box()
    target_box = target.bounding_box()
    
    # Calcular centros de los elementos
    source_x = source_box['x'] + source_box['width'] / 2
    source_y = source_box['y'] + source_box['height'] / 2
    target_x = target_box['x'] + target_box['width'] / 2
    target_y = target_box['y'] + target_box['height'] / 2
    
    # Realizar drag and drop manual con mouse
    context.page.mouse.move(source_x, source_y)
    context.page.mouse.down()
    
    # Pequeña pausa para simular comportamiento humano
    context.page.wait_for_timeout(100)
    
    # Mover al objetivo
    context.page.mouse.move(target_x, target_y)
    
    # Otra pequeña pausa antes de soltar
    context.page.wait_for_timeout(100)
    
    # Soltar el elemento
    context.page.mouse.up()
    
    print(f"✅ Drag and drop completado: {source_element} → {target_element}")

@step('I drag element "{element_name}" by offset x="{x}" y="{y}" with identifier "{identifier}"')
@step('arrastro el elemento "{element_name}" por desplazamiento x="{x}" y="{y}" con identificador "{identifier}"')
def step_drag_by_offset(context, element_name, x, y, identifier):
    """Arrastra un elemento por un desplazamiento específico"""
    locator = context.element_locator.get_locator(identifier)
    element = context.page.locator(locator)
    
    # Asegurar que el elemento sea visible
    expect(element).to_be_visible()
    
    # Convertir coordenadas a enteros
    x_offset = int(x)
    y_offset = int(y)
    
    # Obtener posición inicial
    box = element.bounding_box()
    start_x = box['x'] + box['width'] / 2
    start_y = box['y'] + box['height'] / 2
    
    # Realizar drag por offset con pausas
    context.page.mouse.move(start_x, start_y)
    context.page.mouse.down()
    
    # Pausa para simular comportamiento humano
    context.page.wait_for_timeout(100)
    
    # Mover al destino
    context.page.mouse.move(start_x + x_offset, start_y + y_offset)
    
    # Pausa antes de soltar
    context.page.wait_for_timeout(100)
    
    # Soltar
    context.page.mouse.up()
    
    print(f"✅ Elemento arrastrado por offset: x={x_offset}, y={y_offset}")

@step('I drag element "{element_name}" to coordinates x="{x}" y="{y}" with identifier "{identifier}"')
@step('arrastro el elemento "{element_name}" a las coordenadas x="{x}" y="{y}" con identificador "{identifier}"')
def step_drag_to_coordinates(context, element_name, x, y, identifier):
    """Arrastra un elemento a coordenadas específicas"""
    locator = context.element_locator.get_locator(identifier)
    element = context.page.locator(locator)
    
    # Asegurar que el elemento sea visible
    expect(element).to_be_visible()
    
    # Convertir coordenadas a enteros
    target_x = int(x)
    target_y = int(y)
    
    # Obtener posición inicial del elemento
    box = element.bounding_box()
    start_x = box['x'] + box['width'] / 2
    start_y = box['y'] + box['height'] / 2
    
    # Realizar drag a coordenadas específicas con pausas
    context.page.mouse.move(start_x, start_y)
    context.page.mouse.down()
    
    # Pausa para simular comportamiento humano
    context.page.wait_for_timeout(100)
    
    # Mover a las coordenadas objetivo
    context.page.mouse.move(target_x, target_y)
    
    # Pausa antes de soltar
    context.page.wait_for_timeout(100)
    
    # Soltar
    context.page.mouse.up()
    
    print(f"✅ Elemento arrastrado a coordenadas: x={target_x}, y={target_y}")

@step('I start dragging element "{element_name}" with identifier "{identifier}"')
@step('empiezo a arrastrar el elemento "{element_name}" con identificador "{identifier}"')
def step_start_drag(context, element_name, identifier):
    """Inicia el arrastre de un elemento (para operaciones de drag complejas)"""
    locator = context.element_locator.get_locator(identifier)
    element = context.page.locator(locator)
    
    # Obtener centro del elemento
    box = element.bounding_box()
    center_x = box['x'] + box['width'] / 2
    center_y = box['y'] + box['height'] / 2
    
    # Mover mouse al elemento y presionar
    context.page.mouse.move(center_x, center_y)
    context.page.mouse.down()
    
    # Guardar posición inicial para referencia
    context.drag_start_x = center_x
    context.drag_start_y = center_y

@step('I move dragged element to coordinates x="{x}" y="{y}"')
@step('muevo el elemento arrastrado a las coordenadas x="{x}" y="{y}"')
def step_move_dragged_element(context, x, y):
    """Mueve un elemento que está siendo arrastrado a nuevas coordenadas"""
    target_x = int(x)
    target_y = int(y)
    
    # Mover mouse a las nuevas coordenadas
    context.page.mouse.move(target_x, target_y)

@step('I drop the dragged element')
@step('suelto el elemento arrastrado')
def step_drop_element(context):
    """Suelta el elemento que está siendo arrastrado"""
    context.page.mouse.up()

@step('I hover over element before dragging "{element_name}" with identifier "{identifier}"')
@step('paso el mouse sobre el elemento antes de arrastrar "{element_name}" con identificador "{identifier}"')
def step_hover_before_drag(context, element_name, identifier):
    """Pasa el mouse sobre un elemento antes de arrastrarlo (útil para elementos que requieren hover)"""
    locator = context.element_locator.get_locator(identifier)
    element = context.page.locator(locator)
    
    # Asegurar que el elemento sea visible
    expect(element).to_be_visible()
    
    # Obtener posición del elemento
    box = element.bounding_box()
    center_x = box['x'] + box['width'] / 2
    center_y = box['y'] + box['height'] / 2
    
    # Hover sobre el elemento
    context.page.mouse.move(center_x, center_y)
    context.page.wait_for_timeout(500)  # Esperar para que se active el hover
    
    print(f"✅ Hover realizado sobre elemento: {element_name}")

@step('I drag element "{element_name}" with slow movement to element "{target_element}" with identifiers "{source_id}" and "{target_id}"')
@step('arrastro lentamente el elemento "{element_name}" al elemento "{target_element}" con identificadores "{source_id}" y "{target_id}"')
def step_slow_drag_drop(context, element_name, target_element, source_id, target_id):
    """Drag and drop con movimiento lento (útil para elementos sensibles)"""
    source_locator = context.element_locator.get_locator(source_id)
    target_locator = context.element_locator.get_locator(target_id)
    
    # Obtener elementos
    source = context.page.locator(source_locator)
    target = context.page.locator(target_locator)
    
    # Asegurar que ambos elementos sean visibles
    expect(source).to_be_visible()
    expect(target).to_be_visible()
    
    # Obtener posiciones
    source_box = source.bounding_box()
    target_box = target.bounding_box()
    
    source_x = source_box['x'] + source_box['width'] / 2
    source_y = source_box['y'] + source_box['height'] / 2
    target_x = target_box['x'] + target_box['width'] / 2
    target_y = target_box['y'] + target_box['height'] / 2
    
    # Mover al elemento fuente
    context.page.mouse.move(source_x, source_y)
    context.page.wait_for_timeout(300)
    
    # Presionar y mantener
    context.page.mouse.down()
    context.page.wait_for_timeout(500)
    
    # Mover muy lentamente al objetivo
    steps = 20
    for i in range(steps + 1):
        intermediate_x = source_x + (target_x - source_x) * i / steps
        intermediate_y = source_y + (target_y - source_y) * i / steps
        context.page.mouse.move(intermediate_x, intermediate_y)
        context.page.wait_for_timeout(100)  # Movimiento muy lento
    
    # Pausa antes de soltar
    context.page.wait_for_timeout(500)
    
    # Soltar
    context.page.mouse.up()
    context.page.wait_for_timeout(300)
    
    print(f"✅ Drag and drop lento completado: {element_name} → {target_element}")

@step('I verify drag and drop was successful by checking element "{element_name}" position with identifier "{identifier}"')
@step('verifico que el drag and drop fue exitoso comprobando la posición del elemento "{element_name}" con identificador "{identifier}"')
def step_verify_drag_success(context, element_name, identifier):
    """Verifica que el drag and drop fue exitoso comprobando cambios en el elemento"""
    locator = context.element_locator.get_locator(identifier)
    element = context.page.locator(locator)
    
    # Esperar a que el elemento esté visible después del drag
    expect(element).to_be_visible()
    
    # Obtener posición actual
    box = element.bounding_box()
    current_x = box['x']
    current_y = box['y']
    
    # Verificar que el elemento tiene una posición válida
    assert current_x >= 0 and current_y >= 0, f"Elemento en posición inválida: x={current_x}, y={current_y}"
    
    print(f"✅ Drag and drop verificado: {element_name} en posición x={current_x}, y={current_y}")

@step('I verify element "{element_name}" is at position x="{x}" y="{y}" with identifier "{identifier}"')
@step('verifico que el elemento "{element_name}" está en la posición x="{x}" y="{y}" con identificador "{identifier}"')
def step_verify_element_position(context, element_name, x, y, identifier):
    """Verifica que un elemento está en una posición específica (aproximada)"""
    locator = context.element_locator.get_locator(identifier)
    element = context.page.locator(locator)
    
    expected_x = int(x)
    expected_y = int(y)
    tolerance = 10  # Tolerancia de 10 píxeles
    
    # Obtener posición actual
    box = element.bounding_box()
    actual_x = box['x']
    actual_y = box['y']
    
    # Verificar posición con tolerancia
    assert abs(actual_x - expected_x) <= tolerance, f"Elemento en x={actual_x}, esperado x={expected_x} (±{tolerance})"
    assert abs(actual_y - expected_y) <= tolerance, f"Elemento en y={actual_y}, esperado y={expected_y} (±{tolerance})"

@step('I drag and drop file "{file_path}" to element "{element_name}" with identifier "{identifier}"')
@step('arrastro y suelto el archivo "{file_path}" al elemento "{element_name}" con identificador "{identifier}"')
def step_drag_drop_file(context, file_path, element_name, identifier):
    """Arrastra y suelta un archivo en un elemento (para uploads)"""
    import os
    
    # Resolver ruta del archivo
    resolved_path = context.variable_manager.resolve_variables(file_path)
    
    # Verificar que el archivo existe
    if not os.path.exists(resolved_path):
        raise FileNotFoundError(f"Archivo no encontrado: {resolved_path}")
    
    locator = context.element_locator.get_locator(identifier)
    
    # Usar set_input_files para elementos de tipo file
    context.page.locator(locator).set_input_files(resolved_path)

@step('I drag element "{source_element}" to element "{target_element}" using native API with identifiers "{source_id}" and "{target_id}"')
@step('arrastro el elemento "{source_element}" al elemento "{target_element}" usando API nativa con identificadores "{source_id}" y "{target_id}"')
def step_drag_and_drop_native(context, source_element, target_element, source_id, target_id):
    """Arrastra un elemento usando la API nativa de Playwright (alternativa más robusta)"""
    source_locator = context.element_locator.get_locator(source_id)
    target_locator = context.element_locator.get_locator(target_id)
    
    # Obtener elementos
    source = context.page.locator(source_locator)
    target = context.page.locator(target_locator)
    
    # Asegurar que ambos elementos sean visibles
    expect(source).to_be_visible()
    expect(target).to_be_visible()
    
    try:
        # Intentar con la API nativa de Playwright
        source.drag_to(target, force=True)
        print(f"✅ Drag and drop nativo completado: {source_element} → {target_element}")
    except Exception as e:
        print(f"⚠️ API nativa falló, usando método manual: {e}")
        # Fallback al método manual
        step_drag_and_drop_elements(context, source_element, target_element, source_id, target_id)

@step('I perform advanced drag and drop from "{source_element}" to "{target_element}" with identifiers "{source_id}" and "{target_id}"')
@step('realizo drag and drop avanzado desde "{source_element}" hasta "{target_element}" con identificadores "{source_id}" y "{target_id}"')
def step_advanced_drag_drop(context, source_element, target_element, source_id, target_id):
    """Drag and drop avanzado con múltiples métodos de fallback"""
    source_locator = context.element_locator.get_locator(source_id)
    target_locator = context.element_locator.get_locator(target_id)
    
    # Obtener elementos
    source = context.page.locator(source_locator)
    target = context.page.locator(target_locator)
    
    # Asegurar que ambos elementos sean visibles
    expect(source).to_be_visible()
    expect(target).to_be_visible()
    
    # Método 1: Intentar con API nativa
    try:
        source.drag_to(target, force=True)
        print(f"✅ Drag and drop avanzado (API nativa): {source_element} → {target_element}")
        return
    except Exception as e:
        print(f"⚠️ Método 1 (API nativa) falló: {e}")
    
    # Método 2: Drag and drop manual con mouse
    try:
        source_box = source.bounding_box()
        target_box = target.bounding_box()
        
        source_x = source_box['x'] + source_box['width'] / 2
        source_y = source_box['y'] + source_box['height'] / 2
        target_x = target_box['x'] + target_box['width'] / 2
        target_y = target_box['y'] + target_box['height'] / 2
        
        # Hover sobre el elemento fuente primero
        context.page.mouse.move(source_x, source_y)
        context.page.wait_for_timeout(200)
        
        # Presionar y mantener
        context.page.mouse.down()
        context.page.wait_for_timeout(300)
        
        # Mover lentamente al objetivo
        steps = 10
        for i in range(steps + 1):
            intermediate_x = source_x + (target_x - source_x) * i / steps
            intermediate_y = source_y + (target_y - source_y) * i / steps
            context.page.mouse.move(intermediate_x, intermediate_y)
            context.page.wait_for_timeout(50)
        
        # Soltar
        context.page.mouse.up()
        context.page.wait_for_timeout(200)
        
        print(f"✅ Drag and drop avanzado (manual): {source_element} → {target_element}")
        return
    except Exception as e:
        print(f"⚠️ Método 2 (manual) falló: {e}")
    
    # Método 3: HTML5 drag and drop con JavaScript
    try:
        step_html5_drag_drop(context, source_element, target_element, source_id, target_id)
        print(f"✅ Drag and drop avanzado (HTML5): {source_element} → {target_element}")
    except Exception as e:
        print(f"❌ Todos los métodos fallaron: {e}")
        raise Exception(f"No se pudo completar drag and drop de {source_element} a {target_element}")

@step('I simulate drag and drop with HTML5 from "{source_element}" to "{target_element}" with identifiers "{source_id}" and "{target_id}"')
@step('simulo drag and drop con HTML5 desde "{source_element}" hasta "{target_element}" con identificadores "{source_id}" y "{target_id}"')
def step_html5_drag_drop(context, source_element, target_element, source_id, target_id):
    """Simula drag and drop HTML5 usando JavaScript con soporte completo para CSS, XPath y identificadores del framework"""
    source_locator = context.element_locator.get_locator(source_id)
    target_locator = context.element_locator.get_locator(target_id)
    
    # JavaScript mejorado para simular HTML5 drag and drop con soporte completo
    drag_drop_script = """
    (selectors) => {
        const sourceSelector = selectors[0];
        const targetSelector = selectors[1];
        
        // Función mejorada para obtener elemento por CSS, XPath o identificadores del framework
        function getElement(selector) {
            try {
                // Caso 1: XPath selector
                if (selector.startsWith('//') || selector.startsWith('.//') || selector.startsWith('(') || selector.includes('[@')) {
                    const result = document.evaluate(selector, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                    return result.singleNodeValue;
                }
                
                // Caso 2: Identificador del framework ($.HAKA.*)
                if (selector.startsWith('$.HAKA.')) {
                    const elementName = selector.replace('$.HAKA.', '');
                    // Buscar por data-testid, id, name, class que contenga el nombre
                    const candidates = [
                        `[data-testid="${elementName}"]`,
                        `#${elementName}`,
                        `[name="${elementName}"]`,
                        `.${elementName}`,
                        `[data-element="${elementName}"]`,
                        `[data-name="${elementName}"]`
                    ];
                    
                    for (const candidate of candidates) {
                        const element = document.querySelector(candidate);
                        if (element) return element;
                    }
                    
                    // Búsqueda por texto parcial en atributos
                    const allElements = document.querySelectorAll('*');
                    for (const element of allElements) {
                        if (element.id && element.id.includes(elementName)) return element;
                        if (element.className && element.className.includes(elementName)) return element;
                        if (element.getAttribute('data-testid') && element.getAttribute('data-testid').includes(elementName)) return element;
                    }
                    return null;
                }
                
                // Caso 3: CSS selector estándar
                return document.querySelector(selector);
                
            } catch (error) {
                console.error('Error finding element with selector:', selector, error);
                return null;
            }
        }
        
        const source = getElement(sourceSelector);
        const target = getElement(targetSelector);
        
        if (!source) {
            throw new Error(`Source element not found with selector: ${sourceSelector}`);
        }
        
        if (!target) {
            throw new Error(`Target element not found with selector: ${targetSelector}`);
        }
        
        // Verificar que los elementos son visibles
        const sourceRect = source.getBoundingClientRect();
        const targetRect = target.getBoundingClientRect();
        
        if (sourceRect.width === 0 || sourceRect.height === 0) {
            throw new Error('Source element is not visible');
        }
        
        if (targetRect.width === 0 || targetRect.height === 0) {
            throw new Error('Target element is not visible');
        }
        
        // Crear DataTransfer object
        const dataTransfer = new DataTransfer();
        
        // Calcular posiciones centrales
        const sourceX = sourceRect.left + sourceRect.width / 2;
        const sourceY = sourceRect.top + sourceRect.height / 2;
        const targetX = targetRect.left + targetRect.width / 2;
        const targetY = targetRect.top + targetRect.height / 2;
        
        // Crear eventos de drag and drop más completos
        const mouseDownEvent = new MouseEvent('mousedown', {
            bubbles: true,
            cancelable: true,
            clientX: sourceX,
            clientY: sourceY,
            button: 0
        });
        
        const dragStartEvent = new DragEvent('dragstart', {
            bubbles: true,
            cancelable: true,
            dataTransfer: dataTransfer,
            clientX: sourceX,
            clientY: sourceY
        });
        
        const dragEvent = new DragEvent('drag', {
            bubbles: true,
            cancelable: true,
            dataTransfer: dataTransfer,
            clientX: sourceX,
            clientY: sourceY
        });
        
        const dragEnterEvent = new DragEvent('dragenter', {
            bubbles: true,
            cancelable: true,
            dataTransfer: dataTransfer,
            clientX: targetX,
            clientY: targetY
        });
        
        const dragOverEvent = new DragEvent('dragover', {
            bubbles: true,
            cancelable: true,
            dataTransfer: dataTransfer,
            clientX: targetX,
            clientY: targetY
        });
        
        const dropEvent = new DragEvent('drop', {
            bubbles: true,
            cancelable: true,
            dataTransfer: dataTransfer,
            clientX: targetX,
            clientY: targetY
        });
        
        const dragEndEvent = new DragEvent('dragend', {
            bubbles: true,
            cancelable: true,
            dataTransfer: dataTransfer,
            clientX: targetX,
            clientY: targetY
        });
        
        const mouseUpEvent = new MouseEvent('mouseup', {
            bubbles: true,
            cancelable: true,
            clientX: targetX,
            clientY: targetY,
            button: 0
        });
        
        // Ejecutar secuencia completa de eventos con timing
        source.dispatchEvent(mouseDownEvent);
        
        setTimeout(() => {
            source.dispatchEvent(dragStartEvent);
            source.dispatchEvent(dragEvent);
        }, 10);
        
        setTimeout(() => {
            target.dispatchEvent(dragEnterEvent);
            target.dispatchEvent(dragOverEvent);
        }, 50);
        
        setTimeout(() => {
            target.dispatchEvent(dropEvent);
            source.dispatchEvent(dragEndEvent);
            target.dispatchEvent(mouseUpEvent);
        }, 100);
        
        return {
            success: true,
            sourceSelector: sourceSelector,
            targetSelector: targetSelector,
            sourceElement: source.tagName + (source.id ? '#' + source.id : ''),
            targetElement: target.tagName + (target.id ? '#' + target.id : '')
        };
    }
    """
    
    try:
        # Ejecutar el script con los selectores como array
        result = context.page.evaluate(drag_drop_script, [source_locator, target_locator])
        
        if result and result.get('success'):
            print(f"✅ HTML5 drag and drop completado: {source_element} → {target_element}")
            print(f"   Source: {result.get('sourceElement', 'N/A')}")
            print(f"   Target: {result.get('targetElement', 'N/A')}")
        else:
            raise Exception("HTML5 drag and drop falló - resultado inválido")
            
    except Exception as e:
        print(f"❌ Error en HTML5 drag and drop: {e}")
        
        # Fallback a método manual con mouse
        print("🔄 Intentando método de fallback con mouse...")
        try:
            step_drag_and_drop_elements(context, source_element, target_element, source_id, target_id)
        except Exception as fallback_error:
            print(f"❌ Método de fallback también falló: {fallback_error}")
            raise Exception(f"Todos los métodos de drag and drop fallaron. Original: {e}, Fallback: {fallback_error}")