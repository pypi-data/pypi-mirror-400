#!/usr/bin/env python3
"""
Sugeridor de pasos para archivos .feature
"""
import re
import os
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import difflib

@dataclass
class StepDefinition:
    """Definición de un paso"""
    pattern: str
    description: str
    category: str
    languages: List[str]
    example: str
    file: str

class StepSuggester:
    """Clase para sugerir pasos disponibles en archivos .feature"""
    
    def __init__(self):
        self.steps: List[StepDefinition] = []
        self._load_step_definitions()
    
    def _load_step_definitions(self):
        """Carga todas las definiciones de pasos del framework"""
        
        # Pasos de navegación
        navigation_steps = [
            StepDefinition(
                pattern=r'I go to the url "([^"]*)"',
                description="Navega a una URL específica",
                category="Navegación",
                languages=["en", "es", "mixed"],
                example='I go to the url "https://example.com"',
                file="navigation_steps.py"
            ),
            StepDefinition(
                pattern=r'voy a la url "([^"]*)"',
                description="Navega a una URL específica (español)",
                category="Navegación", 
                languages=["es", "mixed"],
                example='Dado que voy a la url "https://example.com"',
                file="navigation_steps.py"
            ),
            StepDefinition(
                pattern=r'I go back',
                description="Navega hacia atrás en el historial",
                category="Navegación",
                languages=["en", "mixed"],
                example="When I go back",
                file="navigation_steps.py"
            ),
            StepDefinition(
                pattern=r'voy hacia atrás',
                description="Navega hacia atrás en el historial (español)",
                category="Navegación",
                languages=["es", "mixed"],
                example="Cuando voy hacia atrás",
                file="navigation_steps.py"
            ),
            StepDefinition(
                pattern=r'I wait for (\d+) seconds',
                description="Espera un número específico de segundos",
                category="Navegación",
                languages=["en", "mixed"],
                example="And I wait for 5 seconds",
                file="navigation_steps.py"
            ),
            StepDefinition(
                pattern=r'espero (\d+) segundos',
                description="Espera un número específico de segundos (español)",
                category="Navegación",
                languages=["es", "mixed"],
                example="Y espero 5 segundos",
                file="navigation_steps.py"
            ),
        ]
        
        # Pasos de interacción
        interaction_steps = [
            StepDefinition(
                pattern=r'I click on the element "([^"]*)" with identifier "([^"]*)"',
                description="Hace click en un elemento",
                category="Interacción",
                languages=["en", "mixed"],
                example='I click on the element "login button" with identifier "$.LOGIN.login_button"',
                file="interaction_steps.py"
            ),
            StepDefinition(
                pattern=r'hago click en el elemento "([^"]*)" con identificador "([^"]*)"',
                description="Hace click en un elemento (español)",
                category="Interacción",
                languages=["es", "mixed"],
                example='Cuando hago click en el elemento "botón login" con identificador "$.LOGIN.login_button"',
                file="interaction_steps.py"
            ),
            StepDefinition(
                pattern=r'I fill the field "([^"]*)" with "([^"]*)" with identifier "([^"]*)"',
                description="Rellena un campo de texto",
                category="Interacción",
                languages=["en", "mixed"],
                example='I fill the field "username" with "user@test.com" with identifier "$.LOGIN.username_field"',
                file="interaction_steps.py"
            ),
            StepDefinition(
                pattern=r'relleno el campo "([^"]*)" con "([^"]*)" con identificador "([^"]*)"',
                description="Rellena un campo de texto (español)",
                category="Interacción",
                languages=["es", "mixed"],
                example='Cuando relleno el campo "usuario" con "user@test.com" con identificador "$.LOGIN.username_field"',
                file="interaction_steps.py"
            ),
        ]
        
        # Pasos de aserciones
        assertion_steps = [
            StepDefinition(
                pattern=r'I should see the element "([^"]*)" with identifier "([^"]*)"',
                description="Verifica que un elemento sea visible",
                category="Aserciones",
                languages=["en", "mixed"],
                example='Then I should see the element "welcome message" with identifier "$.HOME.welcome_message"',
                file="assertion_steps.py"
            ),
            StepDefinition(
                pattern=r'debería ver el elemento "([^"]*)" con identificador "([^"]*)"',
                description="Verifica que un elemento sea visible (español)",
                category="Aserciones",
                languages=["es", "mixed"],
                example='Entonces debería ver el elemento "mensaje bienvenida" con identificador "$.HOME.welcome_message"',
                file="assertion_steps.py"
            ),
            StepDefinition(
                pattern=r'the element "([^"]*)" should contain the text "([^"]*)" with identifier "([^"]*)"',
                description="Verifica que un elemento contenga un texto específico",
                category="Aserciones",
                languages=["en", "mixed"],
                example='And the element "error message" should contain the text "Invalid credentials" with identifier "$.LOGIN.error_message"',
                file="assertion_steps.py"
            ),
        ]
        
        # Pasos de variables
        variable_steps = [
            StepDefinition(
                pattern=r'I set the variable "([^"]*)" to "([^"]*)"',
                description="Establece una variable con un valor específico",
                category="Variables",
                languages=["en", "mixed"],
                example='Given I set the variable "username" to "testuser"',
                file="variable_steps.py"
            ),
            StepDefinition(
                pattern=r'establezco la variable "([^"]*)" con el valor "([^"]*)"',
                description="Establece una variable con un valor específico (español)",
                category="Variables",
                languages=["es", "mixed"],
                example='Dado que establezco la variable "usuario" con el valor "testuser"',
                file="variable_steps.py"
            ),
            StepDefinition(
                pattern=r'I generate a random string of length (\d+) and store it in variable "([^"]*)"',
                description="Genera una cadena aleatoria y la guarda en una variable",
                category="Variables",
                languages=["en", "mixed"],
                example='And I generate a random string of length 8 and store it in variable "random_id"',
                file="variable_steps.py"
            ),
        ]
        
        # Combinar todos los pasos
        self.steps = navigation_steps + interaction_steps + assertion_steps + variable_steps
    
    def suggest_steps(self, partial_step: str, language: str = "mixed", limit: int = 10) -> List[StepDefinition]:
        """
        Sugiere pasos basados en texto parcial
        
        Args:
            partial_step: Texto parcial del paso
            language: Idioma preferido ("en", "es", "mixed")
            limit: Número máximo de sugerencias
            
        Returns:
            Lista de definiciones de pasos sugeridos
        """
        suggestions = []
        partial_lower = partial_step.lower()
        
        for step in self.steps:
            if language not in step.languages:
                continue
            
            # Buscar coincidencias en el patrón y descripción
            pattern_lower = step.pattern.lower()
            description_lower = step.description.lower()
            
            score = 0
            
            # Coincidencia exacta en el inicio
            if pattern_lower.startswith(partial_lower):
                score += 100
            # Coincidencia parcial
            elif partial_lower in pattern_lower:
                score += 50
            # Coincidencia en la descripción
            elif partial_lower in description_lower:
                score += 25
            
            # Usar difflib para similitud
            similarity = difflib.SequenceMatcher(None, partial_lower, pattern_lower).ratio()
            score += int(similarity * 30)
            
            if score > 0:
                suggestions.append((score, step))
        
        # Ordenar por puntuación y devolver los mejores
        suggestions.sort(key=lambda x: x[0], reverse=True)
        return [step for _, step in suggestions[:limit]]
    
    def get_steps_by_category(self, category: str, language: str = "mixed") -> List[StepDefinition]:
        """
        Obtiene pasos por categoría
        
        Args:
            category: Categoría de pasos
            language: Idioma preferido
            
        Returns:
            Lista de pasos de la categoría especificada
        """
        return [
            step for step in self.steps 
            if step.category == category and language in step.languages
        ]
    
    def get_all_categories(self) -> List[str]:
        """Obtiene todas las categorías disponibles"""
        return list(set(step.category for step in self.steps))
    
    def search_steps(self, query: str, language: str = "mixed") -> List[StepDefinition]:
        """
        Busca pasos por palabra clave
        
        Args:
            query: Palabra clave a buscar
            language: Idioma preferido
            
        Returns:
            Lista de pasos que coinciden con la búsqueda
        """
        query_lower = query.lower()
        results = []
        
        for step in self.steps:
            if language not in step.languages:
                continue
            
            # Buscar en patrón, descripción y ejemplo
            if (query_lower in step.pattern.lower() or 
                query_lower in step.description.lower() or 
                query_lower in step.example.lower()):
                results.append(step)
        
        return results
    
    def validate_step_syntax(self, step_text: str) -> Tuple[bool, Optional[str]]:
        """
        Valida si un paso tiene la sintaxis correcta
        
        Args:
            step_text: Texto del paso a validar
            
        Returns:
            Tupla (es_válido, mensaje_error)
        """
        step_text = step_text.strip()
        
        # Verificar que empiece con palabra clave de Gherkin
        gherkin_keywords = [
            "Given", "When", "Then", "And", "But",
            "Dado", "Cuando", "Entonces", "Y", "Pero",
            "que", "Given que", "When que", "Then que"
        ]
        
        starts_with_keyword = any(
            step_text.startswith(keyword + " ") or step_text == keyword
            for keyword in gherkin_keywords
        )
        
        if not starts_with_keyword:
            return False, f"El paso debe empezar con una palabra clave de Gherkin: {', '.join(gherkin_keywords[:5])}"
        
        # Verificar identificadores de elementos
        if 'with identifier' in step_text or 'con identificador' in step_text:
            identifier_pattern = r'\$\.[A-Z_]+\.[a-zA-Z_]+'
            if not re.search(identifier_pattern, step_text):
                return False, "El identificador debe tener el formato $.ARCHIVO.elemento"
        
        return True, None
    
    def generate_step_documentation(self, output_file: str = "steps_documentation.md"):
        """
        Genera documentación de todos los pasos disponibles
        
        Args:
            output_file: Archivo donde guardar la documentación
        """
        categories = self.get_all_categories()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Documentación de Pasos - Playwright Behave Framework\n\n")
            f.write("Esta documentación contiene todos los pasos disponibles en el framework.\n\n")
            
            for category in sorted(categories):
                f.write(f"## {category}\n\n")
                
                steps_in_category = self.get_steps_by_category(category, "mixed")
                
                for step in steps_in_category:
                    f.write(f"### {step.description}\n\n")
                    f.write(f"**Patrón:** `{step.pattern}`\n\n")
                    f.write(f"**Idiomas:** {', '.join(step.languages)}\n\n")
                    f.write(f"**Ejemplo:**\n```gherkin\n{step.example}\n```\n\n")
                    f.write(f"**Archivo:** `{step.file}`\n\n")
                    f.write("---\n\n")
        
        print(f"✅ Documentación generada en: {output_file}")
    
    def get_step_completion(self, partial_step: str, cursor_position: int) -> List[str]:
        """
        Obtiene sugerencias de autocompletado para editores
        
        Args:
            partial_step: Paso parcial
            cursor_position: Posición del cursor
            
        Returns:
            Lista de sugerencias de autocompletado
        """
        # Extraer la parte antes del cursor
        text_before_cursor = partial_step[:cursor_position]
        
        # Buscar sugerencias
        suggestions = self.suggest_steps(text_before_cursor, limit=5)
        
        # Convertir a formato de autocompletado
        completions = []
        for suggestion in suggestions:
            # Remover regex y convertir a texto simple
            completion = re.sub(r'\([^)]*\)', '"{}"', suggestion.pattern)
            completion = re.sub(r'\(\?\:[^)]*\)', '', completion)
            completions.append(completion)
        
        return completions