import os
import json
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class ElementLocator:
    """Clase para manejar la localización de elementos desde archivos JSON"""
    
    def __init__(self):
        self.json_poms_path = os.getenv('JSON_POMS_PATH', 'json_poms')
        self._cache = {}
    
    def get_locator(self, identifier: str) -> str:
        """
        Obtiene el localizador de un elemento desde los archivos JSON
        
        Args:
            identifier: Identificador en formato $.ARCHIVO.elemento
            
        Returns:
            str: El localizador del elemento
            
        Raises:
            ValueError: Si el identificador no tiene el formato correcto
            FileNotFoundError: Si el archivo JSON no existe
            KeyError: Si el elemento no existe en el archivo
        """
        if not identifier.startswith('$.'):
            raise ValueError(f"El identificador debe empezar con '$.' - Recibido: {identifier}")
        
        # Parsear el identificador: $.ARCHIVO.elemento
        parts = identifier[2:].split('.', 1)
        if len(parts) != 2:
            raise ValueError(f"Formato de identificador inválido. Esperado: $.ARCHIVO.elemento - Recibido: {identifier}")
        
        file_name, element_name = parts
        
        # Cargar el archivo JSON si no está en caché
        if file_name not in self._cache:
            self._load_json_file(file_name)
        
        # Obtener el localizador
        if element_name not in self._cache[file_name]:
            raise KeyError(f"Elemento '{element_name}' no encontrado en el archivo '{file_name}.json'")
        
        return self._cache[file_name][element_name]
    
    def _load_json_file(self, file_name: str):
        """Carga un archivo JSON en el caché"""
        file_path = os.path.join(self.json_poms_path, f"{file_name}.json")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Archivo JSON no encontrado: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self._cache[file_name] = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error al parsear el archivo JSON {file_path}: {e}")
    
    def get_element(self, page, identifier: str):
        """
        Método simplificado: Obtiene directamente el elemento de Playwright desde JSON
        
        Args:
            page: Página de Playwright (context.page)
            identifier: Identificador en formato $.ARCHIVO.elemento
            
        Returns:
            Locator: Elemento de Playwright listo para usar
            
        Example:
            element = context.element_locator.get_element(context.page, "$.LOGIN.username_field")
            element.fill("admin")
        """
        locator = self.get_locator(identifier)
        return page.locator(locator)
    
    def find(self, page, identifier: str):
        """
        Alias más corto para get_element()
        
        Args:
            page: Página de Playwright (context.page)
            identifier: Identificador en formato $.ARCHIVO.elemento
            
        Returns:
            Locator: Elemento de Playwright listo para usar
            
        Example:
            element = context.element_locator.find(context.page, "$.LOGIN.login_button")
            element.click()
        """
        return self.get_element(page, identifier)
    
    def reload_cache(self):
        """Limpia y recarga el caché de archivos JSON"""
        self._cache.clear()