#!/usr/bin/env python3
"""
Steps para interacción avanzada con tablas
"""
from behave import step
from playwright.sync_api import expect

@step('I verify table "{table_name}" has "{expected_rows}" rows with identifier "{identifier}"')
@step('verifico que la tabla "{table_name}" tiene "{expected_rows}" filas con identificador "{identifier}"')
def step_verify_table_rows(context, table_name, expected_rows, identifier):
    """Verifica que una tabla tiene un número específico de filas"""
    locator = context.element_locator.get_locator(identifier)
    expected_count = int(expected_rows)
    
    # Contar filas (excluyendo header)
    rows = context.page.locator(f'{locator} tbody tr')
    actual_count = rows.count()
    
    assert actual_count == expected_count, f"Tabla tiene {actual_count} filas, esperado {expected_count}"

@step('I verify table "{table_name}" has "{expected_columns}" columns with identifier "{identifier}"')
@step('verifico que la tabla "{table_name}" tiene "{expected_columns}" columnas con identificador "{identifier}"')
def step_verify_table_columns(context, table_name, expected_columns, identifier):
    """Verifica que una tabla tiene un número específico de columnas"""
    locator = context.element_locator.get_locator(identifier)
    expected_count = int(expected_columns)
    
    # Contar columnas del header
    headers = context.page.locator(f'{locator} thead th, {locator} tr:first-child td')
    actual_count = headers.count()
    
    assert actual_count == expected_count, f"Tabla tiene {actual_count} columnas, esperado {expected_count}"

@step('I click on table cell at row "{row}" column "{column}" in table "{table_name}" with identifier "{identifier}"')
@step('hago click en la celda de la fila "{row}" columna "{column}" de la tabla "{table_name}" con identificador "{identifier}"')
def step_click_table_cell(context, row, column, table_name, identifier):
    """Hace click en una celda específica de la tabla"""
    locator = context.element_locator.get_locator(identifier)
    row_index = int(row)
    col_index = int(column)
    
    # Hacer click en la celda específica (índices basados en 1)
    cell = context.page.locator(f'{locator} tbody tr:nth-child({row_index}) td:nth-child({col_index})')
    expect(cell).to_be_visible()
    cell.click()

@step('I verify table cell at row "{row}" column "{column}" contains "{expected_text}" in table "{table_name}" with identifier "{identifier}"')
@step('verifico que la celda de la fila "{row}" columna "{column}" contiene "{expected_text}" en la tabla "{table_name}" con identificador "{identifier}"')
def step_verify_table_cell_text(context, row, column, expected_text, table_name, identifier):
    """Verifica que una celda específica contiene un texto"""
    locator = context.element_locator.get_locator(identifier)
    row_index = int(row)
    col_index = int(column)
    resolved_text = context.variable_manager.resolve_variables(expected_text)
    
    # Verificar contenido de la celda
    cell = context.page.locator(f'{locator} tbody tr:nth-child({row_index}) td:nth-child({col_index})')
    expect(cell).to_contain_text(resolved_text)

@step('I sort table "{table_name}" by column "{column_name}" with identifier "{identifier}"')
@step('ordeno la tabla "{table_name}" por la columna "{column_name}" con identificador "{identifier}"')
def step_sort_table_by_column(context, table_name, column_name, identifier):
    """Ordena una tabla haciendo click en el header de una columna"""
    locator = context.element_locator.get_locator(identifier)
    resolved_column = context.variable_manager.resolve_variables(column_name)
    
    # Buscar el header de la columna y hacer click
    header_selectors = [
        f'{locator} thead th:has-text("{resolved_column}")',
        f'{locator} th:has-text("{resolved_column}")',
        f'{locator} .sortable:has-text("{resolved_column}")'
    ]
    
    header_clicked = False
    for selector in header_selectors:
        header = context.page.locator(selector)
        if header.count() > 0:
            header.first.click()
            header_clicked = True
            break
    
    assert header_clicked, f"Header de columna '{resolved_column}' no encontrado"

@step('I filter table "{table_name}" by column "{column_name}" with value "{filter_value}" with identifier "{identifier}"')
@step('filtro la tabla "{table_name}" por la columna "{column_name}" con valor "{filter_value}" con identificador "{identifier}"')
def step_filter_table(context, table_name, column_name, filter_value, identifier):
    """Filtra una tabla por una columna específica"""
    locator = context.element_locator.get_locator(identifier)
    resolved_column = context.variable_manager.resolve_variables(column_name)
    resolved_value = context.variable_manager.resolve_variables(filter_value)
    
    # Buscar campo de filtro para la columna
    filter_selectors = [
        f'{locator} .filter-{resolved_column.lower()}',
        f'{locator} input[data-column="{resolved_column}"]',
        f'{locator} .column-filter input',
        f'input[placeholder*="{resolved_column}"]'
    ]
    
    filter_found = False
    for selector in filter_selectors:
        filter_input = context.page.locator(selector)
        if filter_input.count() > 0:
            filter_input.first.fill(resolved_value)
            filter_input.first.press('Enter')
            filter_found = True
            break
    
    assert filter_found, f"Campo de filtro para columna '{resolved_column}' no encontrado"

@step('I select row "{row_number}" in table "{table_name}" with identifier "{identifier}"')
@step('selecciono la fila "{row_number}" en la tabla "{table_name}" con identificador "{identifier}"')
def step_select_table_row(context, row_number, table_name, identifier):
    """Selecciona una fila específica de la tabla"""
    locator = context.element_locator.get_locator(identifier)
    row_index = int(row_number)
    
    # Buscar checkbox o elemento seleccionable en la fila
    row_selector = f'{locator} tbody tr:nth-child({row_index})'
    
    # Intentar diferentes métodos de selección
    selection_selectors = [
        f'{row_selector} input[type="checkbox"]',
        f'{row_selector} input[type="radio"]',
        f'{row_selector} .select-row',
        row_selector  # Hacer click en la fila completa
    ]
    
    for selector in selection_selectors:
        element = context.page.locator(selector)
        if element.count() > 0:
            element.first.click()
            return
    
    raise AssertionError(f"No se pudo seleccionar la fila {row_index}")

@step('I verify table "{table_name}" row "{row_number}" is selected with identifier "{identifier}"')
@step('verifico que la fila "{row_number}" de la tabla "{table_name}" está seleccionada con identificador "{identifier}"')
def step_verify_row_selected(context, table_name, row_number, identifier):
    """Verifica que una fila específica está seleccionada"""
    locator = context.element_locator.get_locator(identifier)
    row_index = int(row_number)
    
    # Verificar diferentes indicadores de selección
    row_selector = f'{locator} tbody tr:nth-child({row_index})'
    
    selection_indicators = [
        f'{row_selector} input[type="checkbox"]:checked',
        f'{row_selector} input[type="radio"]:checked',
        f'{row_selector}.selected',
        f'{row_selector}.active'
    ]
    
    is_selected = False
    for selector in selection_indicators:
        if context.page.locator(selector).count() > 0:
            is_selected = True
            break
    
    assert is_selected, f"Fila {row_index} no está seleccionada"

@step('I get table cell value at row "{row}" column "{column}" and store in variable "{variable_name}" from table "{table_name}" with identifier "{identifier}"')
@step('obtengo el valor de la celda fila "{row}" columna "{column}" y lo guardo en la variable "{variable_name}" de la tabla "{table_name}" con identificador "{identifier}"')
def step_get_table_cell_value(context, row, column, variable_name, table_name, identifier):
    """Obtiene el valor de una celda y lo guarda en una variable"""
    locator = context.element_locator.get_locator(identifier)
    row_index = int(row)
    col_index = int(column)
    
    # Obtener texto de la celda
    cell = context.page.locator(f'{locator} tbody tr:nth-child({row_index}) td:nth-child({col_index})')
    cell_text = cell.text_content()
    
    # Guardar en variable
    context.variable_manager.set_variable(variable_name, cell_text.strip())

@step('I verify table "{table_name}" contains row with values "{values}" with identifier "{identifier}"')
@step('verifico que la tabla "{table_name}" contiene una fila con valores "{values}" con identificador "{identifier}"')
def step_verify_table_contains_row(context, table_name, values, identifier):
    """Verifica que la tabla contiene una fila con valores específicos"""
    locator = context.element_locator.get_locator(identifier)
    expected_values = [v.strip() for v in values.split(',')]
    
    # Obtener todas las filas
    rows = context.page.locator(f'{locator} tbody tr')
    row_count = rows.count()
    
    # Buscar fila que coincida
    for i in range(row_count):
        row = rows.nth(i)
        cells = row.locator('td')
        cell_count = cells.count()
        
        if cell_count >= len(expected_values):
            row_values = []
            for j in range(len(expected_values)):
                cell_text = cells.nth(j).text_content().strip()
                row_values.append(cell_text)
            
            if row_values == expected_values:
                return  # Fila encontrada
    
    raise AssertionError(f"No se encontró fila con valores {expected_values}")

@step('I edit table cell at row "{row}" column "{column}" with value "{new_value}" in table "{table_name}" with identifier "{identifier}"')
@step('edito la celda de la fila "{row}" columna "{column}" con valor "{new_value}" en la tabla "{table_name}" con identificador "{identifier}"')
def step_edit_table_cell(context, row, column, new_value, table_name, identifier):
    """Edita el valor de una celda de la tabla"""
    locator = context.element_locator.get_locator(identifier)
    row_index = int(row)
    col_index = int(column)
    resolved_value = context.variable_manager.resolve_variables(new_value)
    
    # Hacer doble click en la celda para editarla
    cell = context.page.locator(f'{locator} tbody tr:nth-child({row_index}) td:nth-child({col_index})')
    cell.dblclick()
    
    # Buscar campo de edición
    edit_selectors = [
        f'{locator} tbody tr:nth-child({row_index}) td:nth-child({col_index}) input',
        f'{locator} tbody tr:nth-child({row_index}) td:nth-child({col_index}) textarea',
        f'{locator} .edit-cell input',
        f'{locator} .editable input'
    ]
    
    edit_found = False
    for selector in edit_selectors:
        edit_field = context.page.locator(selector)
        if edit_field.count() > 0:
            edit_field.first.fill(resolved_value)
            edit_field.first.press('Enter')
            edit_found = True
            break
    
    if not edit_found:
        # Intentar edición directa si la celda es contenteditable
        if cell.get_attribute('contenteditable'):
            cell.fill(resolved_value)
        else:
            raise AssertionError("No se pudo editar la celda")

@step('I export table "{table_name}" data and store in variable "{variable_name}" with identifier "{identifier}"')
@step('exporto los datos de la tabla "{table_name}" y los guardo en la variable "{variable_name}" con identificador "{identifier}"')
def step_export_table_data(context, table_name, variable_name, identifier):
    """Exporta todos los datos de la tabla como lista de diccionarios"""
    locator = context.element_locator.get_locator(identifier)
    
    # Obtener headers
    headers = context.page.locator(f'{locator} thead th, {locator} tr:first-child th')
    header_texts = []
    for i in range(headers.count()):
        header_text = headers.nth(i).text_content().strip()
        header_texts.append(header_text)
    
    # Obtener filas de datos
    rows = context.page.locator(f'{locator} tbody tr')
    table_data = []
    
    for i in range(rows.count()):
        row = rows.nth(i)
        cells = row.locator('td')
        row_data = {}
        
        for j in range(min(cells.count(), len(header_texts))):
            cell_text = cells.nth(j).text_content().strip()
            row_data[header_texts[j]] = cell_text
        
        table_data.append(row_data)
    
    # Guardar en variable
    context.variable_manager.set_variable(variable_name, table_data)