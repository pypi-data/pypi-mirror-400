import os
import re
from typing import Any, Dict

class VariableManager:
    """Clase para manejar variables del framework y de entorno"""
    
    def __init__(self):
        self.scenario_variables: Dict[str, Any] = {}
        self.global_variables: Dict[str, Any] = {}
    
    def set_variable(self, name: str, value: Any, scope: str = 'scenario'):
        """
        Establece una variable
        
        Args:
            name: Nombre de la variable
            value: Valor de la variable
            scope: Alcance de la variable ('scenario' o 'global')
        """
        if scope == 'global':
            self.global_variables[name] = value
        else:
            self.scenario_variables[name] = value
    
    def get_variable(self, name: str) -> Any:
        """
        Obtiene el valor de una variable
        
        Args:
            name: Nombre de la variable
            
        Returns:
            El valor de la variable
            
        Raises:
            KeyError: Si la variable no existe
        """
        # Buscar primero en variables de escenario
        if name in self.scenario_variables:
            return self.scenario_variables[name]
        
        # Luego en variables globales
        if name in self.global_variables:
            return self.global_variables[name]
        
        # Finalmente en variables de entorno
        env_value = os.getenv(name)
        if env_value is not None:
            return env_value
        
        raise KeyError(f"Variable '{name}' no encontrada")
    
    def resolve_variables(self, text: str) -> str:
        """
        Resuelve variables en un texto usando el formato ${variable_name}
        
        Args:
            text: Texto que puede contener variables
            
        Returns:
            Texto con las variables resueltas
        """
        if not isinstance(text, str):
            return text
        
        # Patrón para encontrar variables: ${variable_name}
        pattern = r'\$\{([^}]+)\}'
        
        def replace_variable(match):
            var_name = match.group(1)
            try:
                return str(self.get_variable(var_name))
            except KeyError:
                # Si la variable no existe, mantener el texto original
                return match.group(0)
        
        return re.sub(pattern, replace_variable, text)
    
    def clear_scenario_variables(self):
        """Limpia las variables del escenario actual"""
        self.scenario_variables.clear()
    
    def clear_all_variables(self):
        """Limpia todas las variables"""
        self.scenario_variables.clear()
        self.global_variables.clear()