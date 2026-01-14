#!/usr/bin/env python3
"""
Context Helpers - Funciones de utilidad para simplificar steps personalizados
"""

def setup_context_helpers(context):
    """
    Agrega funciones helper al context para simplificar la creación de steps
    """
    
    def find_element(identifier: str):
        """
        Función ultra-simplificada para obtener elementos desde JSON
        
        Args:
            identifier: Identificador en formato $.ARCHIVO.elemento
            
        Returns:
            Locator: Elemento de Playwright listo para usar
            
        Example:
            element = context.find("$.LOGIN.username_field")
            element.fill("admin")
        """
        return context.element_locator.get_element(context.page, identifier)
    
    def find_all_elements(identifier: str):
        """
        Obtiene todos los elementos que coinciden con el selector
        
        Args:
            identifier: Identificador en formato $.ARCHIVO.elemento
            
        Returns:
            List[Locator]: Lista de elementos de Playwright
            
        Example:
            elements = context.find_all("$.PRODUCTS.product_cards")
            for element in elements:
                print(element.text_content())
        """
        locator = context.element_locator.get_locator(identifier)
        return context.page.locator(locator).all()
    
    def click_element(identifier: str, **kwargs):
        """
        Click simplificado en una línea
        
        Args:
            identifier: Identificador en formato $.ARCHIVO.elemento
            **kwargs: Opciones adicionales para click (timeout, button, etc.)
            
        Example:
            context.click("$.LOGIN.login_button")
            context.click("$.MENU.options", button="right")
        """
        element = context.element_locator.get_element(context.page, identifier)
        element.click(**kwargs)
    
    def fill_element(identifier: str, text: str, **kwargs):
        """
        Fill simplificado en una línea
        
        Args:
            identifier: Identificador en formato $.ARCHIVO.elemento
            text: Texto a escribir (se resuelven variables automáticamente)
            **kwargs: Opciones adicionales para fill
            
        Example:
            context.fill("$.LOGIN.username_field", "admin")
            context.fill("$.FORMS.email", "${USER_EMAIL}")
        """
        resolved_text = context.variable_manager.resolve_variables(text)
        element = context.element_locator.get_element(context.page, identifier)
        element.fill(resolved_text, **kwargs)
    
    def get_text(identifier: str) -> str:
        """
        Obtiene texto de un elemento en una línea
        
        Args:
            identifier: Identificador en formato $.ARCHIVO.elemento
            
        Returns:
            str: Texto del elemento
            
        Example:
            message = context.get_text("$.ALERTS.success_message")
        """
        element = context.element_locator.get_element(context.page, identifier)
        return element.text_content().strip()
    
    def is_visible(identifier: str) -> bool:
        """
        Verifica si un elemento está visible
        
        Args:
            identifier: Identificador en formato $.ARCHIVO.elemento
            
        Returns:
            bool: True si está visible, False si no
            
        Example:
            if context.is_visible("$.MODALS.confirmation_dialog"):
                context.click("$.MODALS.accept_button")
        """
        element = context.element_locator.get_element(context.page, identifier)
        return element.is_visible()
    
    def wait_for_element(identifier: str, timeout: int = 30000):
        """
        Espera a que un elemento sea visible
        
        Args:
            identifier: Identificador en formato $.ARCHIVO.elemento
            timeout: Tiempo de espera en milisegundos
            
        Example:
            context.wait_for("$.LOADING.spinner", timeout=10000)
        """
        element = context.element_locator.get_element(context.page, identifier)
        element.wait_for(state="visible", timeout=timeout)
    
    def hover_element(identifier: str, **kwargs):
        """
        Hover simplificado en una línea
        
        Args:
            identifier: Identificador en formato $.ARCHIVO.elemento
            **kwargs: Opciones adicionales para hover
            
        Example:
            context.hover("$.MENU.dropdown_trigger")
        """
        element = context.element_locator.get_element(context.page, identifier)
        element.hover(**kwargs)
    
    def select_option(identifier: str, option: str, **kwargs):
        """
        Selección de opción simplificada
        
        Args:
            identifier: Identificador en formato $.ARCHIVO.elemento
            option: Opción a seleccionar (se resuelven variables)
            **kwargs: Opciones adicionales
            
        Example:
            context.select("$.FORMS.country_dropdown", "Spain")
            context.select("$.FORMS.category", "${SELECTED_CATEGORY}")
        """
        resolved_option = context.variable_manager.resolve_variables(option)
        element = context.element_locator.get_element(context.page, identifier)
        element.select_option(resolved_option, **kwargs)
    
    def check_element(identifier: str, **kwargs):
        """
        Marcar checkbox simplificado
        
        Args:
            identifier: Identificador en formato $.ARCHIVO.elemento
            **kwargs: Opciones adicionales
            
        Example:
            context.check("$.FORMS.terms_checkbox")
        """
        element = context.element_locator.get_element(context.page, identifier)
        element.check(**kwargs)
    
    def uncheck_element(identifier: str, **kwargs):
        """
        Desmarcar checkbox simplificado
        
        Args:
            identifier: Identificador en formato $.ARCHIVO.elemento
            **kwargs: Opciones adicionales
            
        Example:
            context.uncheck("$.FORMS.newsletter_checkbox")
        """
        element = context.element_locator.get_element(context.page, identifier)
        element.uncheck(**kwargs)
    
    # Agregar funciones al context
    context.find = find_element
    context.find_all = find_all_elements
    context.click = click_element
    context.fill = fill_element
    context.get_text = get_text
    context.is_visible = is_visible
    context.wait_for = wait_for_element
    context.hover = hover_element
    context.select = select_option
    context.check = check_element
    context.uncheck = uncheck_element
    
    # Alias adicionales para mayor flexibilidad
    context.element = find_element  # Alias: context.element("$.LOGIN.button")
    context.text = get_text         # Alias: context.text("$.ALERTS.message")
    context.visible = is_visible    # Alias: context.visible("$.MODAL.dialog")


def add_bulk_operations(context):
    """
    Agrega operaciones en lote para múltiples elementos
    """
    
    def fill_form(form_data: dict):
        """
        Rellena múltiples campos de un formulario
        
        Args:
            form_data: Diccionario con identificadores y valores
            
        Example:
            context.fill_form({
                "$.LOGIN.username_field": "admin",
                "$.LOGIN.password_field": "${PASSWORD}",
                "$.LOGIN.remember_checkbox": True
            })
        """
        for identifier, value in form_data.items():
            if isinstance(value, bool):
                if value:
                    context.check(identifier)
                else:
                    context.uncheck(identifier)
            else:
                context.fill(identifier, str(value))
    
    def click_sequence(identifiers: list, delay: int = 500):
        """
        Hace click en una secuencia de elementos con delay
        
        Args:
            identifiers: Lista de identificadores
            delay: Delay entre clicks en milisegundos
            
        Example:
            context.click_sequence([
                "$.MENU.products",
                "$.SUBMENU.electronics",
                "$.PRODUCTS.laptop_category"
            ], delay=1000)
        """
        for i, identifier in enumerate(identifiers):
            context.click(identifier)
            if i < len(identifiers) - 1:  # No delay después del último click
                context.page.wait_for_timeout(delay)
    
    def extract_data(identifiers: dict) -> dict:
        """
        Extrae datos de múltiples elementos
        
        Args:
            identifiers: Diccionario con nombres y identificadores
            
        Returns:
            dict: Datos extraídos
            
        Example:
            data = context.extract_data({
                "title": "$.PRODUCT.title",
                "price": "$.PRODUCT.price",
                "description": "$.PRODUCT.description"
            })
        """
        result = {}
        for name, identifier in identifiers.items():
            result[name] = context.get_text(identifier)
        return result
    
    # Agregar al context
    context.fill_form = fill_form
    context.click_sequence = click_sequence
    context.extract_data = extract_data


def setup_advanced_helpers(context):
    """
    Funciones helper avanzadas para casos complejos
    """
    
    def wait_and_click(identifier: str, timeout: int = 30000, **kwargs):
        """
        Espera a que el elemento sea visible y hace click
        
        Args:
            identifier: Identificador del elemento
            timeout: Tiempo de espera
            **kwargs: Opciones adicionales para click
            
        Example:
            context.wait_and_click("$.DYNAMIC.load_more_button", timeout=10000)
        """
        context.wait_for(identifier, timeout)
        context.click(identifier, **kwargs)
    
    def scroll_and_click(identifier: str, **kwargs):
        """
        Hace scroll al elemento y luego click
        
        Args:
            identifier: Identificador del elemento
            **kwargs: Opciones adicionales para click
            
        Example:
            context.scroll_and_click("$.FOOTER.contact_link")
        """
        element = context.find(identifier)
        element.scroll_into_view_if_needed()
        element.click(**kwargs)
    
    def retry_action(action_func, max_retries: int = 3, delay: int = 1000):
        """
        Reintenta una acción si falla
        
        Args:
            action_func: Función a ejecutar
            max_retries: Número máximo de reintentos
            delay: Delay entre reintentos
            
        Example:
            context.retry_action(
                lambda: context.click("$.UNSTABLE.submit_button"),
                max_retries=5,
                delay=2000
            )
        """
        for attempt in range(max_retries):
            try:
                action_func()
                return  # Éxito, salir
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e  # Último intento, re-lanzar excepción
                context.page.wait_for_timeout(delay)
    
    def conditional_action(identifier: str, action_func, else_func=None):
        """
        Ejecuta una acción solo si el elemento está visible
        
        Args:
            identifier: Identificador del elemento
            action_func: Función a ejecutar si está visible
            else_func: Función a ejecutar si no está visible
            
        Example:
            context.conditional_action(
                "$.MODAL.close_button",
                lambda: context.click("$.MODAL.close_button"),
                lambda: context.logger.info("Modal no visible")
            )
        """
        if context.is_visible(identifier):
            action_func()
        elif else_func:
            else_func()
    
    # Agregar al context
    context.wait_and_click = wait_and_click
    context.scroll_and_click = scroll_and_click
    context.retry_action = retry_action
    context.conditional_action = conditional_action