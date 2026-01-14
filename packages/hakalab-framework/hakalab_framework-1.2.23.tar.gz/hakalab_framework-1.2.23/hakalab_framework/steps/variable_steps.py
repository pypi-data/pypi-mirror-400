#!/usr/bin/env python3
"""
Steps para manejo de variables durante la ejecución
Permite crear, modificar y usar variables dinámicamente en los features
"""
import os
import json
import random
import string
from datetime import datetime, timedelta
from behave import step

@step('creo la variable "{variable_name}" con valor "{value}"')
@step('que creo variable "{variable_name}" = "{value}"')
@step('establezco "{variable_name}" = "{value}"')
@step('I set the variable "{variable_name}" to "{value}"')
@step('establezco la variable "{variable_name}" con el valor "{value}"')
@step('que establezco la variable "{variable_name}" con el valor "{value}"')
def step_create_variable(context, variable_name, value):
    """Crea o actualiza una variable con un valor específico"""
    # Resolver variables existentes en el valor
    if hasattr(context, 'variable_manager'):
        resolved_value = context.variable_manager.resolve_variables(value)
        context.variable_manager.set_variable(variable_name, resolved_value)
    else:
        # Fallback: usar context directamente
        if not hasattr(context, 'test_variables'):
            context.test_variables = {}
        context.test_variables[variable_name] = value
    
    print(f"✅ Variable creada: {variable_name} = '{value}'")

@step('genero una variable "{variable_name}" con texto aleatorio de {length:d} caracteres')
@step('que genero variable aleatoria "{variable_name}" de {length:d} caracteres')
@step('I generate a random string of length {length:d} and store it in variable "{variable_name}"')
@step('genero una cadena aleatoria de longitud {length:d} y la guardo en la variable "{variable_name}"')
@step('que genero una cadena aleatoria de longitud {length:d} y la guardo en la variable "{variable_name}"')
def step_generate_random_text_variable(context, variable_name, length):
    """Genera una variable con texto aleatorio"""
    random_text = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    if hasattr(context, 'variable_manager'):
        context.variable_manager.set_variable(variable_name, random_text)
    else:
        if not hasattr(context, 'test_variables'):
            context.test_variables = {}
        context.test_variables[variable_name] = random_text
    
    print(f"✅ Variable aleatoria generada: {variable_name} = '{random_text}'")

@step('genero una variable "{variable_name}" con número aleatorio entre {min_val:d} y {max_val:d}')
@step('I generate a random number between {min_val:d} and {max_val:d} and store it in variable "{variable_name}"')
@step('genero un número aleatorio entre {min_val:d} y {max_val:d} y lo guardo en la variable "{variable_name}"')
@step('que genero un número aleatorio entre {min_val:d} y {max_val:d} y lo guardo en la variable "{variable_name}"')
def step_generate_random_number_variable(context, variable_name, min_val, max_val):
    """Genera una variable con número aleatorio"""
    random_number = random.randint(min_val, max_val)
    
    if hasattr(context, 'variable_manager'):
        context.variable_manager.set_variable(variable_name, str(random_number))
    else:
        if not hasattr(context, 'test_variables'):
            context.test_variables = {}
        context.test_variables[variable_name] = str(random_number)
    
    print(f"✅ Variable numérica generada: {variable_name} = {random_number}")

@step('genero una variable "{variable_name}" con timestamp actual')
@step('que genero timestamp en variable "{variable_name}"')
@step('I get the current timestamp and store it in variable "{variable_name}"')
@step('obtengo el timestamp actual y lo guardo en la variable "{variable_name}"')
@step('que obtengo el timestamp actual y lo guardo en la variable "{variable_name}"')
def step_generate_timestamp_variable(context, variable_name):
    """Genera una variable con timestamp actual"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if hasattr(context, 'variable_manager'):
        context.variable_manager.set_variable(variable_name, timestamp)
    else:
        if not hasattr(context, 'test_variables'):
            context.test_variables = {}
        context.test_variables[variable_name] = timestamp
    
    print(f"✅ Variable timestamp generada: {variable_name} = '{timestamp}'")

@step('genero una variable "{variable_name}" con fecha actual en formato "{date_format}"')
@step('I get the current date and store it in variable "{variable_name}"')
@step('obtengo la fecha actual y la guardo en la variable "{variable_name}"')
@step('que obtengo la fecha actual y la guardo en la variable "{variable_name}"')
def step_generate_date_variable(context, variable_name, date_format="%Y-%m-%d"):
    """Genera una variable con fecha en formato específico"""
    # Formatos comunes: %Y-%m-%d, %d/%m/%Y, %Y%m%d, etc.
    current_date = datetime.now().strftime(date_format)
    
    if hasattr(context, 'variable_manager'):
        context.variable_manager.set_variable(variable_name, current_date)
    else:
        if not hasattr(context, 'test_variables'):
            context.test_variables = {}
        context.test_variables[variable_name] = current_date
    
    print(f"✅ Variable fecha generada: {variable_name} = '{current_date}' (formato: {date_format})")

@step('concateno las variables "{var1}" y "{var2}" en la variable "{result_var}"')
@step('que concateno "{var1}" + "{var2}" = "{result_var}"')
@step('I concatenate "{text1}" and "{text2}" and store it in variable "{variable_name}"')
@step('concateno "{text1}" y "{text2}" y lo guardo en la variable "{variable_name}"')
@step('que concateno "{text1}" y "{text2}" y lo guardo en la variable "{variable_name}"')
def step_concatenate_variables(context, var1, var2, result_var):
    """Concatena dos variables en una nueva variable"""
    # Obtener valores de las variables
    value1 = ""
    value2 = ""
    
    if hasattr(context, 'variable_manager'):
        value1 = context.variable_manager.get_variable(var1, "")
        value2 = context.variable_manager.get_variable(var2, "")
        result = str(value1) + str(value2)
        context.variable_manager.set_variable(result_var, result)
    else:
        if hasattr(context, 'test_variables'):
            value1 = context.test_variables.get(var1, "")
            value2 = context.test_variables.get(var2, "")
        result = str(value1) + str(value2)
        if not hasattr(context, 'test_variables'):
            context.test_variables = {}
        context.test_variables[result_var] = result
    
    print(f"✅ Variables concatenadas: {result_var} = '{value1}' + '{value2}' = '{result}'")

@step('incremento la variable numérica "{variable_name}" en {increment:d}')
@step('que sumo {increment:d} a la variable "{variable_name}"')
def step_increment_numeric_variable(context, variable_name, increment):
    """Incrementa una variable numérica"""
    current_value = 0
    
    if hasattr(context, 'variable_manager'):
        current_value = int(context.variable_manager.get_variable(variable_name, "0"))
        new_value = current_value + increment
        context.variable_manager.set_variable(variable_name, str(new_value))
    else:
        if hasattr(context, 'test_variables') and variable_name in context.test_variables:
            current_value = int(context.test_variables[variable_name])
        new_value = current_value + increment
        if not hasattr(context, 'test_variables'):
            context.test_variables = {}
        context.test_variables[variable_name] = str(new_value)
    
    print(f"✅ Variable incrementada: {variable_name} = {current_value} + {increment} = {new_value}")

@step('muestro el valor de la variable "{variable_name}"')
@step('que imprimo la variable "{variable_name}"')
@step('I print the variable "{variable_name}"')
@step('imprimo la variable "{variable_name}"')
@step('que imprimo la variable "{variable_name}"')
def step_print_variable_value(context, variable_name):
    """Muestra el valor actual de una variable"""
    value = ""
    
    if hasattr(context, 'variable_manager'):
        try:
            value = context.variable_manager.get_variable(variable_name)
        except KeyError:
            value = "VARIABLE_NO_ENCONTRADA"
    elif hasattr(context, 'test_variables') and variable_name in context.test_variables:
        value = context.test_variables[variable_name]
    else:
        value = "VARIABLE_NO_ENCONTRADA"
    
    print(f"📋 Variable '{variable_name}' = '{value}'")

@step('verifico que la variable "{variable_name}" contiene "{expected_value}"')
@step('que la variable "{variable_name}" debe contener "{expected_value}"')
def step_verify_variable_contains(context, variable_name, expected_value):
    """Verifica que una variable contiene un valor específico"""
    actual_value = ""
    
    if hasattr(context, 'variable_manager'):
        actual_value = context.variable_manager.get_variable(variable_name, "")
        expected_value = context.variable_manager.resolve_variables(expected_value)
    elif hasattr(context, 'test_variables') and variable_name in context.test_variables:
        actual_value = context.test_variables[variable_name]
    
    assert str(expected_value) in str(actual_value), f"Variable '{variable_name}' = '{actual_value}' no contiene '{expected_value}'"
    print(f"✅ Variable verificada: '{variable_name}' contiene '{expected_value}'")

@step('verifico que la variable "{variable_name}" es igual a "{expected_value}"')
@step('que la variable "{variable_name}" debe ser "{expected_value}"')
def step_verify_variable_equals(context, variable_name, expected_value):
    """Verifica que una variable es exactamente igual a un valor"""
    actual_value = ""
    
    if hasattr(context, 'variable_manager'):
        actual_value = context.variable_manager.get_variable(variable_name, "")
        expected_value = context.variable_manager.resolve_variables(expected_value)
    elif hasattr(context, 'test_variables') and variable_name in context.test_variables:
        actual_value = context.test_variables[variable_name]
    
    assert str(actual_value) == str(expected_value), f"Variable '{variable_name}' = '{actual_value}' no es igual a '{expected_value}'"
    print(f"✅ Variable verificada: '{variable_name}' = '{expected_value}'")

@step('guardo el texto del elemento "{selector}" en la variable "{variable_name}"')
@step('que extraigo texto de "{selector}" a variable "{variable_name}"')
def step_extract_text_to_variable(context, selector, variable_name):
    """Extrae el texto de un elemento y lo guarda en una variable"""
    # Obtener elemento
    if hasattr(context, 'get_element'):
        element = context.get_element(selector)
    else:
        element = context.page.locator(selector)
    
    # Extraer texto
    text_content = element.text_content()
    
    # Guardar en variable
    if hasattr(context, 'variable_manager'):
        context.variable_manager.set_variable(variable_name, text_content)
    else:
        if not hasattr(context, 'test_variables'):
            context.test_variables = {}
        context.test_variables[variable_name] = text_content
    
    print(f"✅ Texto extraído a variable: {variable_name} = '{text_content}'")

@step('guardo el atributo "{attribute}" del elemento "{selector}" en la variable "{variable_name}"')
def step_extract_attribute_to_variable(context, attribute, selector, variable_name):
    """Extrae un atributo de un elemento y lo guarda en una variable"""
    # Obtener elemento
    if hasattr(context, 'get_element'):
        element = context.get_element(selector)
    else:
        element = context.page.locator(selector)
    
    # Extraer atributo
    attribute_value = element.get_attribute(attribute)
    
    # Guardar en variable
    if hasattr(context, 'variable_manager'):
        context.variable_manager.set_variable(variable_name, attribute_value or "")
    else:
        if not hasattr(context, 'test_variables'):
            context.test_variables = {}
        context.test_variables[variable_name] = attribute_value or ""
    
    print(f"✅ Atributo extraído a variable: {variable_name} = '{attribute_value}'")

@step('muestro todas las variables actuales')
@step('que listo todas las variables')
def step_list_all_variables(context):
    """Muestra todas las variables actuales"""
    print("\n📋 Variables actuales:")
    
    if hasattr(context, 'variable_manager'):
        variables = context.variable_manager.get_all_variables()
        if variables:
            for name, value in variables.items():
                print(f"   {name} = '{value}'")
        else:
            print("   (No hay variables definidas)")
    elif hasattr(context, 'test_variables'):
        if context.test_variables:
            for name, value in context.test_variables.items():
                print(f"   {name} = '{value}'")
        else:
            print("   (No hay variables definidas)")
    else:
        print("   (No hay variables definidas)")

@step('limpio todas las variables')
@step('que borro todas las variables')
@step('I clear all scenario variables')
@step('limpio todas las variables del escenario')
@step('que limpio todas las variables del escenario')
def step_clear_all_variables(context):
    """Limpia todas las variables"""
    if hasattr(context, 'variable_manager'):
        context.variable_manager.clear_scenario_variables()
    elif hasattr(context, 'test_variables'):
        context.test_variables.clear()
    
    print("✅ Todas las variables han sido limpiadas")

@step('copio la variable "{source_var}" a "{target_var}"')
@step('que duplico variable "{source_var}" como "{target_var}"')
def step_copy_variable(context, source_var, target_var):
    """Copia el valor de una variable a otra"""
    source_value = ""
    
    if hasattr(context, 'variable_manager'):
        source_value = context.variable_manager.get_variable(source_var, "")
        context.variable_manager.set_variable(target_var, source_value)
    elif hasattr(context, 'test_variables') and source_var in context.test_variables:
        source_value = context.test_variables[source_var]
        context.test_variables[target_var] = source_value
    
    print(f"✅ Variable copiada: {target_var} = {source_var} = '{source_value}'")