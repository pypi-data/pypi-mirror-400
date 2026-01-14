#!/usr/bin/env python3
"""
Steps específicos para automatización de Salesforce
Incluye Lightning Experience, Classic, y componentes específicos de Salesforce
"""
from behave import step
from playwright.sync_api import expect
import time
import re

@step('I wait for Salesforce Lightning to load')
@step('espero a que cargue Salesforce Lightning')
def step_wait_lightning_load(context):
    """Espera a que Salesforce Lightning termine de cargar completamente"""
    # Esperar a que desaparezca el spinner de carga
    context.page.wait_for_selector('.slds-spinner', state='hidden', timeout=30000)
    
    # Esperar a que aparezca la navegación principal
    context.page.wait_for_selector('.slds-global-header', state='visible', timeout=15000)
    
    # Esperar un poco más para asegurar carga completa
    time.sleep(2)

@step('I navigate to Salesforce app "{app_name}"')
@step('navego a la aplicación de Salesforce "{app_name}"')
def step_navigate_to_app(context, app_name):
    """Navega a una aplicación específica en Salesforce"""
    resolved_app = context.variable_manager.resolve_variables(app_name)
    
    # Hacer click en el App Launcher
    app_launcher = context.page.locator('.slds-icon-waffle')
    app_launcher.click()
    
    # Esperar a que aparezca el modal del App Launcher
    context.page.wait_for_selector('.slds-modal__container', state='visible')
    
    # Buscar y hacer click en la aplicación
    app_link = context.page.locator(f'a[data-label="{resolved_app}"], .slds-app-launcher__tile-title:has-text("{resolved_app}")')
    if app_link.count() > 0:
        app_link.first.click()
    else:
        # Si no está visible, buscar en "View All"
        view_all = context.page.locator('button:has-text("View All")')
        if view_all.count() > 0:
            view_all.click()
            time.sleep(1)
            app_link = context.page.locator(f'a[data-label="{resolved_app}"], .slds-app-launcher__tile-title:has-text("{resolved_app}")')
            app_link.first.click()

@step('I navigate to Salesforce object "{object_name}"')
@step('navego al objeto de Salesforce "{object_name}"')
def step_navigate_to_object(context, object_name):
    """Navega a un objeto específico (Account, Contact, etc.)"""
    resolved_object = context.variable_manager.resolve_variables(object_name)
    
    # Hacer click en el menú de navegación
    nav_menu = context.page.locator('.slds-global-header__item--search button, .slds-context-bar__item--tab button')
    if nav_menu.count() > 0:
        nav_menu.first.click()
    
    # Buscar el objeto en el menú
    object_link = context.page.locator(f'a[title*="{resolved_object}"], .slds-nav-vertical__action:has-text("{resolved_object}")')
    if object_link.count() > 0:
        object_link.first.click()
    else:
        # Usar la URL directa si no se encuentra en el menú
        current_url = context.page.url
        base_url = re.match(r'(https://[^/]+)', current_url).group(1)
        object_url = f"{base_url}/lightning/o/{resolved_object}/list"
        context.page.goto(object_url)

@step('I create new Salesforce record for object "{object_name}"')
@step('creo un nuevo registro de Salesforce para el objeto "{object_name}"')
def step_create_new_record(context, object_name):
    """Inicia la creación de un nuevo registro"""
    resolved_object = context.variable_manager.resolve_variables(object_name)
    
    # Buscar botón "New" en diferentes ubicaciones
    new_button_selectors = [
        'a[title="New"]',
        'button[title="New"]',
        '.slds-button:has-text("New")',
        '.forceActionLink[title="New"]'
    ]
    
    button_clicked = False
    for selector in new_button_selectors:
        button = context.page.locator(selector)
        if button.count() > 0:
            button.first.click()
            button_clicked = True
            break
    
    if not button_clicked:
        raise AssertionError(f"No se encontró el botón 'New' para crear registro de {resolved_object}")
    
    # Esperar a que aparezca el formulario
    context.page.wait_for_selector('.slds-modal__container, .record-form', state='visible')

@step('I fill Salesforce field "{field_name}" with "{value}"')
@step('relleno el campo de Salesforce "{field_name}" con "{value}"')
def step_fill_salesforce_field(context, field_name, value):
    """Rellena un campo específico en Salesforce (maneja diferentes tipos)"""
    resolved_field = context.variable_manager.resolve_variables(field_name)
    resolved_value = context.variable_manager.resolve_variables(value)
    
    # Diferentes selectores para campos de Salesforce
    field_selectors = [
        f'input[data-field-name="{resolved_field}"]',
        f'input[name="{resolved_field}"]',
        f'textarea[data-field-name="{resolved_field}"]',
        f'lightning-input[data-field="{resolved_field}"] input',
        f'lightning-textarea[data-field="{resolved_field}"] textarea',
        f'[data-target-selection-name="{resolved_field}"] input'
    ]
    
    field_found = False
    for selector in field_selectors:
        field = context.page.locator(selector)
        if field.count() > 0:
            field.first.fill(resolved_value)
            field_found = True
            break
    
    if not field_found:
        # Buscar por label asociado
        label = context.page.locator(f'label:has-text("{resolved_field}")')
        if label.count() > 0:
            # Encontrar el input asociado al label
            label_for = label.get_attribute('for')
            if label_for:
                field = context.page.locator(f'#{label_for}')
                field.fill(resolved_value)
                field_found = True
    
    assert field_found, f"Campo '{resolved_field}' no encontrado"

@step('I select Salesforce picklist "{field_name}" option "{option}"')
@step('selecciono la opción "{option}" del picklist "{field_name}" de Salesforce')
def step_select_picklist(context, field_name, option):
    """Selecciona una opción de un picklist de Salesforce"""
    resolved_field = context.variable_manager.resolve_variables(field_name)
    resolved_option = context.variable_manager.resolve_variables(option)
    
    # Buscar el picklist
    picklist_selectors = [
        f'lightning-combobox[data-field="{resolved_field}"] button',
        f'select[data-field-name="{resolved_field}"]',
        f'[data-target-selection-name="{resolved_field}"] button'
    ]
    
    picklist_found = False
    for selector in picklist_selectors:
        picklist = context.page.locator(selector)
        if picklist.count() > 0:
            # Hacer click para abrir
            picklist.first.click()
            time.sleep(0.5)
            
            # Seleccionar la opción
            option_selectors = [
                f'lightning-base-combobox-item[data-value="{resolved_option}"]',
                f'option[value="{resolved_option}"]',
                f'.slds-listbox__option:has-text("{resolved_option}")'
            ]
            
            for opt_selector in option_selectors:
                option_element = context.page.locator(opt_selector)
                if option_element.count() > 0:
                    option_element.first.click()
                    picklist_found = True
                    break
            
            if picklist_found:
                break
    
    assert picklist_found, f"Picklist '{resolved_field}' o opción '{resolved_option}' no encontrada"

@step('I search and select Salesforce lookup "{field_name}" with "{search_term}"')
@step('busco y selecciono el lookup "{field_name}" de Salesforce con "{search_term}"')
def step_search_lookup(context, field_name, search_term):
    """Busca y selecciona un valor en un campo lookup de Salesforce"""
    resolved_field = context.variable_manager.resolve_variables(field_name)
    resolved_term = context.variable_manager.resolve_variables(search_term)
    
    # Buscar el campo lookup
    lookup_selectors = [
        f'input[data-field-name="{resolved_field}"]',
        f'lightning-lookup[data-field="{resolved_field}"] input',
        f'[data-target-selection-name="{resolved_field}"] input'
    ]
    
    lookup_found = False
    for selector in lookup_selectors:
        lookup_input = context.page.locator(selector)
        if lookup_input.count() > 0:
            # Escribir el término de búsqueda
            lookup_input.first.fill(resolved_term)
            time.sleep(1)
            
            # Esperar a que aparezcan los resultados
            context.page.wait_for_selector('.slds-listbox__option, .lookup__menu-item', state='visible', timeout=5000)
            
            # Seleccionar el primer resultado
            result = context.page.locator('.slds-listbox__option, .lookup__menu-item').first
            result.click()
            lookup_found = True
            break
    
    assert lookup_found, f"Campo lookup '{resolved_field}' no encontrado"

@step('I save Salesforce record')
@step('guardo el registro de Salesforce')
def step_save_record(context):
    """Guarda el registro actual en Salesforce"""
    save_selectors = [
        'button[title="Save"]',
        'button:has-text("Save")',
        '.slds-button--brand:has-text("Save")',
        'input[value="Save"]'
    ]
    
    save_clicked = False
    for selector in save_selectors:
        save_button = context.page.locator(selector)
        if save_button.count() > 0:
            save_button.first.click()
            save_clicked = True
            break
    
    assert save_clicked, "Botón 'Save' no encontrado"
    
    # Esperar a que se complete el guardado
    context.page.wait_for_selector('.slds-spinner', state='hidden', timeout=15000)

@step('I verify Salesforce record field "{field_name}" contains "{expected_value}"')
@step('verifico que el campo "{field_name}" del registro de Salesforce contiene "{expected_value}"')
def step_verify_record_field(context, field_name, expected_value):
    """Verifica el valor de un campo en un registro de Salesforce"""
    resolved_field = context.variable_manager.resolve_variables(field_name)
    resolved_value = context.variable_manager.resolve_variables(expected_value)
    
    # Buscar el campo en la vista de detalle
    field_selectors = [
        f'[data-target-selection-name="{resolved_field}"] .slds-form-element__static',
        f'lightning-formatted-text[data-field="{resolved_field}"]',
        f'.test-id__{resolved_field} .slds-form-element__static',
        f'span[title*="{resolved_field}"]'
    ]
    
    field_found = False
    for selector in field_selectors:
        field_element = context.page.locator(selector)
        if field_element.count() > 0:
            field_text = field_element.first.text_content()
            assert resolved_value in field_text, f"Campo '{resolved_field}' contiene '{field_text}', esperado '{resolved_value}'"
            field_found = True
            break
    
    assert field_found, f"Campo '{resolved_field}' no encontrado en la vista de detalle"

@step('I click Salesforce tab "{tab_name}"')
@step('hago click en la pestaña "{tab_name}" de Salesforce')
def step_click_tab(context, tab_name):
    """Hace click en una pestaña específica de Salesforce"""
    resolved_tab = context.variable_manager.resolve_variables(tab_name)
    
    tab_selectors = [
        f'a[title="{resolved_tab}"]',
        f'.slds-tabs_default__item a:has-text("{resolved_tab}")',
        f'lightning-tab[title="{resolved_tab}"]'
    ]
    
    tab_clicked = False
    for selector in tab_selectors:
        tab = context.page.locator(selector)
        if tab.count() > 0:
            tab.first.click()
            tab_clicked = True
            break
    
    assert tab_clicked, f"Pestaña '{resolved_tab}' no encontrada"

@step('I wait for Salesforce toast message "{message_type}"')
@step('espero el mensaje toast de Salesforce "{message_type}"')
def step_wait_toast_message(context, message_type):
    """Espera a que aparezca un mensaje toast de Salesforce"""
    resolved_type = context.variable_manager.resolve_variables(message_type)
    
    toast_selectors = {
        'success': '.slds-notify--toast.slds-theme--success',
        'error': '.slds-notify--toast.slds-theme--error',
        'warning': '.slds-notify--toast.slds-theme--warning',
        'info': '.slds-notify--toast.slds-theme--info'
    }
    
    selector = toast_selectors.get(resolved_type.lower(), '.slds-notify--toast')
    context.page.wait_for_selector(selector, state='visible', timeout=10000)

@step('I close Salesforce toast messages')
@step('cierro los mensajes toast de Salesforce')
def step_close_toast_messages(context):
    """Cierra todos los mensajes toast visibles"""
    close_buttons = context.page.locator('.slds-notify--toast .slds-notify__close')
    count = close_buttons.count()
    
    for i in range(count):
        try:
            close_buttons.nth(i).click()
            time.sleep(0.2)
        except:
            pass  # Ignorar si el toast ya se cerró automáticamente

@step('I switch to Salesforce Classic view')
@step('cambio a la vista clásica de Salesforce')
def step_switch_to_classic(context):
    """Cambia a Salesforce Classic desde Lightning"""
    # Buscar el switcher en el perfil
    profile_menu = context.page.locator('.slds-global-actions__item--menu button')
    if profile_menu.count() > 0:
        profile_menu.click()
        
        # Buscar opción "Switch to Salesforce Classic"
        classic_link = context.page.locator('a:has-text("Switch to Salesforce Classic")')
        if classic_link.count() > 0:
            classic_link.click()

@step('I switch to Salesforce Lightning view')
@step('cambio a la vista Lightning de Salesforce')
def step_switch_to_lightning(context):
    """Cambia a Lightning desde Salesforce Classic"""
    # Buscar el switcher en Classic
    lightning_link = context.page.locator('a:has-text("Switch to Lightning Experience")')
    if lightning_link.count() > 0:
        lightning_link.click()

@step('I open Salesforce record "{record_id}" for object "{object_name}"')
@step('abro el registro "{record_id}" de Salesforce para el objeto "{object_name}"')
def step_open_record_by_id(context, record_id, object_name):
    """Abre un registro específico por su ID"""
    resolved_id = context.variable_manager.resolve_variables(record_id)
    resolved_object = context.variable_manager.resolve_variables(object_name)
    
    # Construir URL del registro
    current_url = context.page.url
    base_url = re.match(r'(https://[^/]+)', current_url).group(1)
    record_url = f"{base_url}/lightning/r/{resolved_object}/{resolved_id}/view"
    
    context.page.goto(record_url)
    
    # Esperar a que cargue el registro
    context.page.wait_for_selector('.slds-page-header, .record-header', state='visible')

@step('I edit Salesforce record')
@step('edito el registro de Salesforce')
def step_edit_record(context):
    """Inicia la edición del registro actual"""
    edit_selectors = [
        'button[title="Edit"]',
        'button:has-text("Edit")',
        '.slds-button:has-text("Edit")'
    ]
    
    edit_clicked = False
    for selector in edit_selectors:
        edit_button = context.page.locator(selector)
        if edit_button.count() > 0:
            edit_button.first.click()
            edit_clicked = True
            break
    
    assert edit_clicked, "Botón 'Edit' no encontrado"
    
    # Esperar a que aparezca el formulario de edición
    context.page.wait_for_selector('.slds-modal__container, .record-form', state='visible')

@step('I delete Salesforce record')
@step('elimino el registro de Salesforce')
def step_delete_record(context):
    """Elimina el registro actual"""
    # Buscar menú de acciones
    actions_menu = context.page.locator('button[title="Show more actions"], .slds-button_icon-more')
    if actions_menu.count() > 0:
        actions_menu.first.click()
        
        # Buscar opción Delete
        delete_option = context.page.locator('a[title="Delete"], .slds-dropdown__item:has-text("Delete")')
        if delete_option.count() > 0:
            delete_option.first.click()
            
            # Confirmar eliminación
            confirm_delete = context.page.locator('button:has-text("Delete")')
            if confirm_delete.count() > 0:
                confirm_delete.first.click()

@step('I search Salesforce global search with "{search_term}"')
@step('busco en la búsqueda global de Salesforce con "{search_term}"')
def step_global_search(context, search_term):
    """Realiza una búsqueda global en Salesforce"""
    resolved_term = context.variable_manager.resolve_variables(search_term)
    
    # Buscar el campo de búsqueda global
    search_selectors = [
        'input[placeholder*="Search"]',
        '.slds-global-search input',
        'input[data-aura-class="uiInput"]'
    ]
    
    search_found = False
    for selector in search_selectors:
        search_input = context.page.locator(selector)
        if search_input.count() > 0:
            search_input.first.fill(resolved_term)
            search_input.first.press('Enter')
            search_found = True
            break
    
    assert search_found, "Campo de búsqueda global no encontrado"
    
    # Esperar resultados
    context.page.wait_for_selector('.slds-lookup__list, .search-results', state='visible')